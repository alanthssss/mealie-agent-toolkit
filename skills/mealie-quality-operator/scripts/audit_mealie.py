#!/usr/bin/env python3
"""Deterministic quality gates for Mealie-like recipe and meal-plan JSON."""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Iterable


DEFAULT_POLICY: dict[str, Any] = {
    "require_food_links": True,
    "require_quantities": True,
    "require_units_for_quantities": True,
    "check_instruction_coverage": True,
    "duplicate_food_similarity": 0.8,
    "pantry_foods": ["水", "盐", "食用油", "黑胡椒"],
    "aliases": {},
}


@dataclass(frozen=True)
class Issue:
    severity: str
    code: str
    path: str
    message: str


def normalize(value: Any) -> str:
    text = unicodedata.normalize("NFKC", str(value or "")).casefold()
    return re.sub(r"[\s\-_·,，。.;；:：/\\()（）\[\]【】]+", "", text)


def first(mapping: dict[str, Any], keys: Iterable[str], default: Any = None) -> Any:
    for key in keys:
        if key in mapping and mapping[key] is not None:
            return mapping[key]
    return default


def object_name(value: Any) -> str:
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, dict):
        return str(first(value, ("name", "label", "title"), "")).strip()
    return ""


def object_id(value: Any) -> str:
    if isinstance(value, dict):
        return str(first(value, ("id", "uuid", "value"), "")).strip()
    return ""


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_policy(path: Path | None) -> dict[str, Any]:
    policy = dict(DEFAULT_POLICY)
    if path:
        loaded = load_json(path)
        if not isinstance(loaded, dict):
            raise ValueError("policy must be a JSON object")
        policy.update(loaded)
    return policy


def canonicalizer(policy: dict[str, Any]):
    aliases = policy.get("aliases", {})
    lookup: dict[str, str] = {}
    if isinstance(aliases, dict):
        for canonical, variants in aliases.items():
            canonical_norm = normalize(canonical)
            lookup[canonical_norm] = canonical_norm
            for variant in variants if isinstance(variants, list) else []:
                lookup[normalize(variant)] = canonical_norm

    def canonical(value: Any) -> str:
        normalized = normalize(value)
        return lookup.get(normalized, normalized)

    return canonical


def recipe_name(recipe: dict[str, Any]) -> str:
    return str(first(recipe, ("name", "title", "recipeName"), "")).strip()


def recipe_ingredients(recipe: dict[str, Any]) -> list[dict[str, Any]]:
    raw = first(recipe, ("recipeIngredient", "recipeIngredients", "ingredients"), [])
    return [item for item in raw if isinstance(item, dict)] if isinstance(raw, list) else []


def instruction_text(recipe: dict[str, Any]) -> str:
    raw = first(recipe, ("recipeInstructions", "instructions", "steps", "method"), [])
    parts: list[str] = []

    def visit(value: Any) -> None:
        if isinstance(value, str):
            parts.append(value)
        elif isinstance(value, list):
            for child in value:
                visit(child)
        elif isinstance(value, dict):
            for key in ("title", "summary", "text", "description", "instruction"):
                if value.get(key):
                    visit(value[key])

    visit(raw)
    return "\n".join(parts).strip()


def catalog_maps(data: Any) -> tuple[dict[str, str], dict[str, str]]:
    if not data:
        return {}, {}
    if isinstance(data, dict):
        values = first(data, ("items", "foods", "data"), [])
        if not isinstance(values, list):
            values = [data]
    elif isinstance(data, list):
        values = data
    else:
        values = []
    by_name: dict[str, str] = {}
    by_id: dict[str, str] = {}
    for item in values:
        if not isinstance(item, dict):
            continue
        name = object_name(item)
        item_id = object_id(item)
        if name:
            by_name[normalize(name)] = item_id
        if item_id:
            by_id[item_id] = normalize(name)
    return by_name, by_id


def linked_list_issues(recipe: dict[str, Any]) -> list[Issue]:
    issues: list[Issue] = []
    fields = {
        "categories": ("recipeCategory", "categories", "recipeCategories"),
        "tags": ("tags", "recipeTags"),
        "tools": ("tools", "recipeTools"),
    }
    expectations = recipe.get("auditExpectations", {})
    expected_filters = expectations.get("filters", {}) if isinstance(expectations, dict) else {}
    for label, keys in fields.items():
        raw = first(recipe, keys)
        expected = expected_filters.get(label, []) if isinstance(expected_filters, dict) else []
        if raw is None and not expected:
            continue
        if raw is None:
            raw = []
        if not isinstance(raw, list):
            issues.append(Issue("error", "filter.collection.invalid", label, f"{label} must be a list of linked objects"))
            continue
        for index, item in enumerate(raw):
            if not isinstance(item, dict) or not object_id(item) or not object_name(item):
                issues.append(Issue(
                    "error",
                    "filter.link.missing",
                    f"{label}[{index}]",
                    f"{label} value must contain both a stable ID and name for filtering",
                ))
        actual_ids = {object_id(item) for item in raw if isinstance(item, dict) and object_id(item)}
        actual_names = {normalize(object_name(item)) for item in raw if isinstance(item, dict) and object_name(item)}
        for index, item in enumerate(expected if isinstance(expected, list) else []):
            expected_id = object_id(item)
            expected_name = object_name(item)
            matched = expected_id in actual_ids if expected_id else normalize(expected_name) in actual_names
            if not matched:
                issues.append(Issue(
                    "error",
                    "filter.expected_link.missing",
                    f"auditExpectations.filters.{label}[{index}]",
                    f"expected linked {label} object {expected_name or expected_id!r} is absent",
                ))
    return issues


def audit_recipe(
    recipe: dict[str, Any],
    policy: dict[str, Any],
    catalog: Any = None,
    prefix: str = "recipe",
) -> list[Issue]:
    issues: list[Issue] = []
    canonical = canonicalizer(policy)
    by_name, by_id = catalog_maps(catalog)
    name = recipe_name(recipe)
    if not name:
        issues.append(Issue("error", "recipe.name.missing", f"{prefix}.name", "recipe name is blank"))

    ingredients = recipe_ingredients(recipe)
    if not ingredients:
        issues.append(Issue("error", "ingredient.list.empty", f"{prefix}.ingredients", "recipe has no structured ingredients"))

    linked_foods: list[tuple[int, str, str]] = []
    seen: dict[tuple[str, str], list[int]] = {}
    for index, ingredient in enumerate(ingredients):
        path = f"{prefix}.ingredients[{index}]"
        quantity = first(ingredient, ("quantity", "amount", "qty"))
        unit = first(ingredient, ("unit", "recipeUnit"))
        food = first(ingredient, ("food", "ingredient", "recipeFood"))
        food_name = object_name(food)
        food_id = object_id(food)
        unit_name = object_name(unit)
        note = str(first(ingredient, ("note", "display", "displayText", "originalText"), "")).strip()
        expected = first(ingredient, ("expectedFood", "expected_food"))

        row_has_content = any(value not in (None, "", {}) for value in (quantity, unit, food, note))
        if policy.get("require_food_links", True) and row_has_content and not isinstance(food, dict):
            issues.append(Issue("error", "ingredient.food.missing", f"{path}.food", "ingredient is not linked to a food object"))
        elif isinstance(food, dict) and not food_name and not food_id:
            issues.append(Issue("error", "ingredient.food.incomplete", f"{path}.food", "linked food has neither name nor stable ID"))

        if policy.get("require_quantities", True) and quantity in (None, ""):
            issues.append(Issue("error", "ingredient.quantity.missing", f"{path}.quantity", "ingredient quantity is missing"))
        if policy.get("require_units_for_quantities", True) and quantity not in (None, "") and not unit_name:
            issues.append(Issue("error", "ingredient.unit.missing", f"{path}.unit", "numeric quantity has no unit"))

        note_norm = normalize(note)
        if note and re.search(r"\d", unicodedata.normalize("NFKC", note)):
            repeats_food = bool(food_name and normalize(food_name) in note_norm)
            repeats_unit = bool(unit_name and normalize(unit_name) in note_norm)
            if repeats_food or repeats_unit:
                issues.append(Issue(
                    "error",
                    "ingredient.display.duplicated",
                    f"{path}.note",
                    "note/display repeats structured quantity, unit, or food fields",
                ))

        if expected and food_name:
            expected_name = object_name(expected) or str(expected)
            expected_id = object_id(expected)
            name_mismatch = canonical(expected_name) != canonical(food_name)
            id_mismatch = bool(expected_id and expected_id != food_id)
            if name_mismatch or id_mismatch:
                issues.append(Issue(
                    "error",
                    "ingredient.food.expected_mismatch",
                    f"{path}.food",
                    f"expected food {expected_name!r}/{expected_id or '(any id)'}, selected {food_name!r}/{food_id or '(no id)'}",
                ))

        if catalog is not None and food_name:
            normalized_food = normalize(food_name)
            if normalized_food not in by_name:
                issues.append(Issue("error", "ingredient.food.catalog_mismatch", f"{path}.food", f"food {food_name!r} is absent from the supplied catalog"))
            elif food_id and by_name[normalized_food] and by_name[normalized_food] != food_id:
                issues.append(Issue("error", "ingredient.food.catalog_mismatch", f"{path}.food", f"food name {food_name!r} resolves to a different catalog ID"))
            if food_id and food_id in by_id and by_id[food_id] != normalized_food:
                issues.append(Issue("error", "ingredient.food.catalog_mismatch", f"{path}.food", "food ID resolves to a different catalog name"))

        if food_name:
            canonical_food = canonical(food_name)
            canonical_unit = canonical(unit_name)
            linked_foods.append((index, canonical_food, food_name))
            seen.setdefault((canonical_food, canonical_unit), []).append(index)

    for (food_name, unit_name), indexes in seen.items():
        if len(indexes) > 1:
            issues.append(Issue(
                "warning",
                "ingredient.duplicate",
                f"{prefix}.ingredients",
                f"duplicate canonical food/unit rows at indexes {indexes}: {food_name}/{unit_name or '(no unit)'}",
            ))

    method = instruction_text(recipe)
    if not method:
        issues.append(Issue("error", "instructions.missing", f"{prefix}.instructions", "recipe has no usable instruction text"))
    elif policy.get("check_instruction_coverage", True):
        method_norm = normalize(method)
        pantry = {canonical(item) for item in policy.get("pantry_foods", [])}
        aliases = policy.get("aliases", {}) if isinstance(policy.get("aliases"), dict) else {}
        for index, canonical_food, display_food in linked_foods:
            if canonical_food in pantry:
                continue
            variants = [display_food]
            for alias_canonical, alias_values in aliases.items():
                if canonical(alias_canonical) == canonical_food:
                    variants.extend(alias_values if isinstance(alias_values, list) else [])
            if not any(normalize(variant) in method_norm for variant in variants if normalize(variant)):
                issues.append(Issue(
                    "warning",
                    "instructions.ingredient_uncovered",
                    f"{prefix}.ingredients[{index}]",
                    f"core ingredient {display_food!r} is not mentioned in the method",
                ))

    issues.extend(linked_list_issues(recipe))
    return issues


def recipes_from(data: Any) -> list[dict[str, Any]]:
    if isinstance(data, list):
        return [item for item in data if isinstance(item, dict)]
    if isinstance(data, dict):
        raw = first(data, ("items", "recipes", "data"))
        if isinstance(raw, list):
            return [item for item in raw if isinstance(item, dict)]
        return [data]
    return []


def audit_collection(data: Any, policy: dict[str, Any], catalog: Any = None) -> tuple[list[Issue], dict[str, Any]]:
    recipes = recipes_from(data)
    issues: list[Issue] = []
    canonical = canonicalizer(policy)
    signatures: list[set[str]] = []
    for index, recipe in enumerate(recipes):
        issues.extend(audit_recipe(recipe, policy, catalog, prefix=f"recipes[{index}]"))
        signatures.append({canonical(object_name(first(row, ("food", "ingredient", "recipeFood")))) for row in recipe_ingredients(recipe) if object_name(first(row, ("food", "ingredient", "recipeFood")))})

    threshold = float(policy.get("duplicate_food_similarity", 0.8))
    duplicate_pairs: list[dict[str, Any]] = []
    for left in range(len(recipes)):
        for right in range(left + 1, len(recipes)):
            union = signatures[left] | signatures[right]
            if len(union) < 2:
                continue
            score = len(signatures[left] & signatures[right]) / len(union)
            if score >= threshold:
                candidate = {
                    "left": recipe_name(recipes[left]),
                    "right": recipe_name(recipes[right]),
                    "ingredient_jaccard": round(score, 3),
                }
                duplicate_pairs.append(candidate)
                issues.append(Issue(
                    "warning",
                    "recipe.duplicate_candidate",
                    f"recipes[{left}],recipes[{right}]",
                    f"possible duplicate: {candidate['left']!r} vs {candidate['right']!r} ({score:.0%} ingredient overlap)",
                ))
    return issues, {"recipes": len(recipes), "duplicate_candidates": duplicate_pairs}


def audit_plan(data: Any, days: int | None, meals_per_day: int | None, people: int | None) -> tuple[list[Issue], dict[str, Any]]:
    if isinstance(data, list):
        entries = [item for item in data if isinstance(item, dict)]
    elif isinstance(data, dict):
        raw = first(data, ("items", "entries", "mealplans", "data"), [])
        entries = [item for item in raw if isinstance(item, dict)] if isinstance(raw, list) else []
    else:
        entries = []
    issues: list[Issue] = []
    recipe_ids: set[str] = set()
    actual_servings = 0.0
    for index, entry in enumerate(entries):
        recipe = first(entry, ("recipe", "recipeSummary"))
        recipe_id = object_id(recipe) or str(first(entry, ("recipeId", "recipe_id"), "")).strip()
        recipe_title = object_name(recipe) or str(first(entry, ("title", "recipeName"), "")).strip()
        if not recipe_id:
            issues.append(Issue("error", "plan.recipe_link.missing", f"entries[{index}].recipe", f"meal occurrence {recipe_title or index!r} has no recipe ID"))
        else:
            recipe_ids.add(recipe_id)
        servings = first(entry, ("servings", "people", "portionCount"), people or 0)
        try:
            actual_servings += float(servings or 0)
        except (TypeError, ValueError):
            issues.append(Issue("error", "plan.servings.invalid", f"entries[{index}].servings", f"invalid servings value {servings!r}"))

    expected_occurrences = days * meals_per_day if days is not None and meals_per_day is not None else None
    expected_servings = expected_occurrences * people if expected_occurrences is not None and people is not None else None
    if expected_occurrences is not None and len(entries) != expected_occurrences:
        issues.append(Issue("error", "plan.occurrences.mismatch", "entries", f"expected {expected_occurrences} meal occurrences, found {len(entries)}"))
    if expected_servings is not None and actual_servings != expected_servings:
        issues.append(Issue("error", "plan.servings.mismatch", "entries", f"expected {expected_servings} servings, found {actual_servings:g}"))
    return issues, {
        "meal_occurrences": len(entries),
        "servings": actual_servings,
        "unique_recipe_ids": len(recipe_ids),
        "expected_occurrences": expected_occurrences,
        "expected_servings": expected_servings,
    }


def render(issues: list[Issue], summary: dict[str, Any], output_format: str) -> None:
    payload = {
        "passed": not any(issue.severity == "error" for issue in issues),
        "errors": sum(issue.severity == "error" for issue in issues),
        "warnings": sum(issue.severity == "warning" for issue in issues),
        "summary": summary,
        "issues": [asdict(issue) for issue in issues],
    }
    if output_format == "json":
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return
    print(f"errors={payload['errors']} warnings={payload['warnings']}")
    for issue in issues:
        print(f"{issue.severity.upper():7} {issue.code:38} {issue.path}: {issue.message}")
    print("summary=" + json.dumps(summary, ensure_ascii=False, sort_keys=True))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("recipe", "collection", "plan"))
    parser.add_argument("input", type=Path, help="Mealie-like JSON input")
    parser.add_argument("--policy", type=Path, help="JSON policy override")
    parser.add_argument("--catalog", type=Path, help="food catalog JSON used for exact ID/name validation")
    parser.add_argument("--strict", action="store_true", help="make warnings fail the command")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    parser.add_argument("--days", type=int)
    parser.add_argument("--meals-per-day", type=int)
    parser.add_argument("--people", type=int)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        data = load_json(args.input)
        policy = load_policy(args.policy)
        catalog = load_json(args.catalog) if args.catalog else None
        if args.mode == "recipe":
            recipes = recipes_from(data)
            if len(recipes) != 1:
                raise ValueError(f"recipe mode requires exactly one recipe, found {len(recipes)}")
            issues = audit_recipe(recipes[0], policy, catalog)
            summary = {"recipes": 1}
        elif args.mode == "collection":
            issues, summary = audit_collection(data, policy, catalog)
        else:
            issues, summary = audit_plan(data, args.days, args.meals_per_day, args.people)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"audit input error: {exc}", file=sys.stderr)
        return 2

    render(issues, summary, args.format)
    has_errors = any(issue.severity == "error" for issue in issues)
    has_warnings = any(issue.severity == "warning" for issue in issues)
    return 1 if has_errors or (args.strict and has_warnings) else 0


if __name__ == "__main__":
    raise SystemExit(main())
