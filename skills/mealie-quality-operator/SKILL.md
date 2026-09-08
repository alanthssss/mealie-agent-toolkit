---
name: mealie-quality-operator
description: Safely create, update, audit, and reconcile Mealie recipes, foods, units, organizers, meal plans, and shopping data. Use for Mealie operations where structured ingredient links, recipe-method consistency, filters, duplicate prevention, or post-save verification matter.
license: MIT
metadata:
  author: mealie-agent-toolkit contributors
  version: "0.1.0"
---

# Mealie Quality Operator

Operate Mealie as structured data, not as a form-filling exercise. Preserve user intent, use stable object identities, and do not report completion until saved state has been read back and audited.

The bundled audit scripts require Python 3.10+. Live operations require access to a Mealie instance through an MCP server, its REST API, or an authenticated browser.

## Choose the operating path

1. Prefer a purpose-built Mealie MCP tool when available.
2. Otherwise use the instance's live `/openapi.json` and authenticated REST API.
3. Use browser control only when neither structured interface is available. After browser edits, reopen the saved object and verify every field.

Never invent credentials or request broader access than the task needs. Treat creation and updates as writes; treat merging and deletion as destructive operations requiring exact target resolution and explicit authorization.

## Required workflow

### Inspect

- Read the target object and the relevant food, unit, category, tag, and tool catalogs before editing.
- Record stable IDs when the interface provides them. Do not select the first fuzzy search result.
- For a multi-recipe plan, distinguish meal occurrences, servings, and unique recipes before calculating totals.

### Build a complete draft

- Keep the recipe name free of administrative prefixes such as `月计划` unless the user explicitly wants them.
- Each ingredient row must have an intentional quantity, unit when applicable, linked food object, and preparation note only when the note adds information.
- Do not copy the formatted ingredient string into the note/display field. Mealie already renders quantity, unit, and food.
- Reuse the same canonical food object for the same ingredient across recipes.
- Merge accidental duplicate ingredient rows unless separate rows represent genuinely different uses and the distinction is preserved in notes or sections.
- Write instructions for the actual ingredient list. Do not reuse a generic method mentioning absent foods or omitting core foods.

### Run the pre-save gate

For recipe writes, serialize the draft to JSON and run:

```bash
python3 scripts/audit_mealie.py recipe draft.json --policy assets/policy.example.json --strict
```

For a batch, run collection audit as well:

```bash
python3 scripts/audit_mealie.py collection recipes.json --policy assets/policy.example.json --strict
```

Do not save while the audit has errors. Resolve warnings when `--strict` is used. When local serialization is impossible, apply the equivalent checklist manually before clicking Save; inspect every row from first to last.

### Save and verify

- Write once after the draft passes.
- Fetch or reopen the saved recipe immediately.
- Run the same recipe audit on the returned representation.
- Confirm every requested category, tag, tool, and food is a linked object, not merely visible text.
- Exercise the requested filters against the saved record and confirm it appears in every expected result.
- For collections, rerun duplicate and plan reconciliation checks after all writes.

If verification fails, keep the item incomplete, correct it, and repeat read-after-write verification. Stop after two failed correction attempts on the same invariant and report the exact blocker rather than repeatedly mutating data.

## Modes and references

- For field rules, severity, known failure patterns, and the manual gate, read [references/quality-gates.md](references/quality-gates.md).
- For the JSON shapes accepted by the deterministic auditor and intent annotations such as `expectedFood`, read [references/audit-schema.md](references/audit-schema.md) before building an adapter or CI integration.
- For API/MCP/browser responsibilities and version handling, read [references/integration-contract.md](references/integration-contract.md) when connecting to or implementing a Mealie adapter.
- For month/week plans, recipe counts, servings, and shopping reconciliation, read [references/meal-plan-reconciliation.md](references/meal-plan-reconciliation.md).
- Use [assets/policy.example.json](assets/policy.example.json) as a starting policy; copy and customize it outside the skill when household aliases or pantry exclusions differ.

## Completion evidence

Report the number of recipes inspected, created, updated, and unchanged; pre-save and post-save audit results; duplicate candidates; plan occurrence and serving totals; and filters actually tested. Do not use “all done” when any target was skipped, unverified, or only visually assumed.
