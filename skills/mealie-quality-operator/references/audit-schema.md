# Audit input schema

The auditor accepts native Mealie-like keys and a small set of non-persistent intent annotations. Strip annotations before sending a payload to Mealie if its API rejects unknown fields.

## Recipe

```json
{
  "name": "清蒸鲈鱼配西兰花",
  "recipeIngredient": [
    {
      "quantity": 1,
      "unit": {"id": "unit-id", "name": "条"},
      "food": {"id": "bass-id", "name": "鲈鱼"},
      "expectedFood": {"id": "bass-id", "name": "鲈鱼"},
      "note": "处理干净"
    }
  ],
  "recipeInstructions": [
    {"text": "鲈鱼处理干净，西兰花切小朵；分别蒸熟。"}
  ],
  "recipeCategory": [{"id": "dinner-id", "name": "晚餐"}],
  "tags": [{"id": "simple-id", "name": "简单"}],
  "tools": [{"id": "steamer-id", "name": "蒸锅"}],
  "auditExpectations": {
    "filters": {
      "categories": [{"id": "dinner-id", "name": "晚餐"}],
      "tags": [{"id": "simple-id", "name": "简单"}],
      "tools": [{"id": "steamer-id", "name": "蒸锅"}]
    }
  }
}
```

`expectedFood` is the intended catalog object captured before selection. It closes the gap between “a valid food is linked” and “the correct food is linked.” Prefer both ID and name. A name-only expectation still prevents near-match substitutions such as `水` → `水芹` and `鸡蛋` → `鸡蛋果`.

`auditExpectations.filters` lists the relationships the user requested. The auditor verifies that each expected category, tag, or tool exists in the saved structured arrays. The live adapter must additionally execute each filter query after saving.

## Collection

Collection mode accepts a JSON array or an object whose `items`, `recipes`, or `data` property is an array of recipes. It runs every recipe gate and then detects duplicate candidates using canonical ingredient-set overlap.

## Meal plan

Plan mode accepts a JSON array or an object whose `items`, `entries`, `mealplans`, or `data` property is an array. Each occurrence should contain a linked recipe object or `recipeId`, plus `servings` when it differs from the CLI `--people` value.

```bash
python3 scripts/audit_mealie.py plan plan.json \
  --days 30 --meals-per-day 3 --people 2 --strict
```

The result reports meal occurrences, total servings, and unique recipe IDs separately.
