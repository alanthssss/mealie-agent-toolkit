import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills" / "mealie-quality-operator" / "scripts" / "audit_mealie.py"
SPEC = importlib.util.spec_from_file_location("audit_mealie", SCRIPT)
audit = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = audit
SPEC.loader.exec_module(audit)


POLICY = {
    **audit.DEFAULT_POLICY,
    "aliases": {"燕麦片": ["燕麦"], "鸡蛋": ["蛋"]},
}


def ingredient(quantity, unit, food, note="", expected=None):
    row = {
        "quantity": quantity,
        "unit": {"id": f"unit-{unit}", "name": unit},
        "food": food,
        "note": note,
    }
    if expected:
        row["expectedFood"] = expected
    return row


class RecipeAuditTests(unittest.TestCase):
    def test_valid_recipe_passes(self):
        recipe = {
            "name": "香蕉燕麦粥",
            "recipeIngredient": [
                ingredient(100, "克", {"id": "oat", "name": "燕麦片"}),
                ingredient(1, "根", {"id": "banana", "name": "香蕉"}),
                ingredient(400, "毫升", {"id": "milk", "name": "牛奶"}),
            ],
            "recipeInstructions": [{"text": "燕麦片和牛奶煮稠，加入切片香蕉。"}],
            "recipeCategory": [{"id": "breakfast", "name": "早餐"}],
        }
        self.assertEqual(audit.audit_recipe(recipe, POLICY), [])

    def test_missing_first_food_is_blocking(self):
        recipe = {
            "name": "香蕉燕麦",
            "recipeIngredient": [
                {"quantity": 100, "unit": {"id": "g", "name": "克"}, "food": None, "note": "燕麦片"},
                ingredient(1, "根", {"id": "banana", "name": "香蕉"}),
            ],
            "recipeInstructions": ["燕麦和香蕉煮熟。"],
        }
        codes = {item.code for item in audit.audit_recipe(recipe, POLICY)}
        self.assertIn("ingredient.food.missing", codes)

    def test_expected_water_cannot_resolve_to_water_celery(self):
        recipe = {
            "name": "清汤",
            "recipeIngredient": [ingredient(800, "毫升", {"id": "water-celery", "name": "水芹"}, expected="水")],
            "recipeInstructions": ["加入水煮开。"],
        }
        codes = {item.code for item in audit.audit_recipe(recipe, POLICY)}
        self.assertIn("ingredient.food.expected_mismatch", codes)

    def test_expected_egg_cannot_resolve_to_eggfruit(self):
        recipe = {
            "name": "煮鸡蛋",
            "recipeIngredient": [ingredient(2, "个", {"id": "eggfruit", "name": "鸡蛋果"}, expected="鸡蛋")],
            "recipeInstructions": ["鸡蛋煮熟。"],
        }
        codes = {item.code for item in audit.audit_recipe(recipe, POLICY)}
        self.assertIn("ingredient.food.expected_mismatch", codes)

    def test_expected_food_id_must_match_even_when_name_matches(self):
        recipe = {
            "name": "牛奶",
            "recipeIngredient": [ingredient(400, "毫升", {"id": "wrong-milk", "name": "牛奶"}, expected={"id": "canonical-milk", "name": "牛奶"})],
            "recipeInstructions": ["牛奶加热。"],
        }
        codes = {item.code for item in audit.audit_recipe(recipe, POLICY)}
        self.assertIn("ingredient.food.expected_mismatch", codes)

    def test_display_string_must_not_duplicate_structured_fields(self):
        recipe = {
            "name": "红薯牛奶",
            "recipeIngredient": [ingredient(500, "克", {"id": "sweet-potato", "name": "红薯"}, "500克 红薯")],
            "recipeInstructions": ["红薯蒸熟。"],
        }
        codes = {item.code for item in audit.audit_recipe(recipe, POLICY)}
        self.assertIn("ingredient.display.duplicated", codes)

    def test_unlinked_filter_value_is_blocking(self):
        recipe = {
            "name": "全麦吐司",
            "recipeIngredient": [ingredient(4, "片", {"id": "toast", "name": "全麦吐司"})],
            "recipeInstructions": ["全麦吐司烤热。"],
            "tags": ["简单"],
        }
        codes = {item.code for item in audit.audit_recipe(recipe, POLICY)}
        self.assertIn("filter.link.missing", codes)

    def test_missing_expected_filter_link_is_blocking(self):
        recipe = {
            "name": "全麦吐司",
            "recipeIngredient": [ingredient(4, "片", {"id": "toast", "name": "全麦吐司"})],
            "recipeInstructions": ["全麦吐司烤热。"],
            "tags": [{"id": "fast", "name": "快手"}],
            "auditExpectations": {"filters": {"tags": [{"id": "simple", "name": "简单"}]}},
        }
        codes = {item.code for item in audit.audit_recipe(recipe, POLICY)}
        self.assertIn("filter.expected_link.missing", codes)

    def test_absent_expected_filter_collection_is_blocking(self):
        recipe = {
            "name": "全麦吐司",
            "recipeIngredient": [ingredient(4, "片", {"id": "toast", "name": "全麦吐司"})],
            "recipeInstructions": ["全麦吐司烤热。"],
            "auditExpectations": {"filters": {"categories": [{"id": "breakfast", "name": "早餐"}]}},
        }
        codes = {item.code for item in audit.audit_recipe(recipe, POLICY)}
        self.assertIn("filter.expected_link.missing", codes)

    def test_unrelated_method_is_detected(self):
        recipe = {
            "name": "全麦吐司",
            "recipeIngredient": [
                ingredient(4, "片", {"id": "toast", "name": "全麦吐司"}),
                ingredient(2, "个", {"id": "egg", "name": "鸡蛋"}),
            ],
            "recipeInstructions": ["燕麦粥加热，薯类提前煮好。"],
        }
        codes = [item.code for item in audit.audit_recipe(recipe, POLICY)]
        self.assertGreaterEqual(codes.count("instructions.ingredient_uncovered"), 2)


class CollectionAuditTests(unittest.TestCase):
    def test_reordered_title_duplicate_is_a_candidate(self):
        base = [
            ingredient(100, "克", {"id": "oat", "name": "燕麦片"}),
            ingredient(1, "根", {"id": "banana", "name": "香蕉"}),
        ]
        recipes = [
            {"name": "燕麦香蕉", "ingredients": base, "instructions": ["燕麦和香蕉混合。"]},
            {"name": "香蕉燕麦", "ingredients": list(reversed(base)), "instructions": ["香蕉加入燕麦。"]},
        ]
        issues, summary = audit.audit_collection(recipes, POLICY)
        self.assertIn("recipe.duplicate_candidate", {item.code for item in issues})
        self.assertEqual(len(summary["duplicate_candidates"]), 1)


class PlanAuditTests(unittest.TestCase):
    def test_occurrences_servings_and_unique_recipes_are_distinct(self):
        entries = [
            {"recipe": {"id": "a", "name": "早餐A"}, "servings": 2},
            {"recipe": {"id": "a", "name": "早餐A"}, "servings": 2},
            {"recipe": {"id": "b", "name": "午餐B"}, "servings": 2},
        ]
        issues, summary = audit.audit_plan(entries, days=1, meals_per_day=3, people=2)
        self.assertEqual(issues, [])
        self.assertEqual(summary["meal_occurrences"], 3)
        self.assertEqual(summary["servings"], 6)
        self.assertEqual(summary["unique_recipe_ids"], 2)


if __name__ == "__main__":
    unittest.main()
