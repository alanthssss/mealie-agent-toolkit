# Recipe quality gates

Use these gates for every recipe create or update. Errors block saving. Warnings block saving in strict mode.

## Structural gates

| Code | Condition | Default severity |
|---|---|---|
| `recipe.name.missing` | Recipe name is blank | error |
| `ingredient.food.missing` | Ingredient has display text but no linked food | error |
| `ingredient.food.incomplete` | Linked food has neither stable ID nor usable name | error |
| `ingredient.quantity.missing` | Quantified planning mode has no quantity | error |
| `ingredient.unit.missing` | A numeric quantity lacks a unit | error |
| `ingredient.display.duplicated` | Note/display repeats quantity, unit, or food | error |
| `ingredient.food.catalog_mismatch` | Food name or ID disagrees with the selected catalog | error |
| `ingredient.duplicate` | Same canonical food/unit appears more than once without a distinguishing use | warning |
| `instructions.missing` | No usable method text | error |
| `instructions.ingredient_uncovered` | A core ingredient is absent from the method | warning |
| `instructions.unknown_food` | Method references a catalog food not present in ingredients | warning |

## Semantic gates

1. Exact identity beats fuzzy similarity. `水` is not `水芹`; `鸡蛋` is not `鸡蛋果`.
2. A displayed phrase is not a relationship. Filters and shopping aggregation depend on linked food, organizer, and tool objects.
3. Ingredient notes describe preparation or use, such as `切丁` or `分两次加入`. They must not contain `400 毫升 牛奶` when quantity, unit, and food already hold those values.
4. Repeated foods should normally be combined. Keep separate rows only when the recipe genuinely needs separate uses and encode the reason.
5. Methods must be recipe-specific. A toast recipe must not contain boilerplate about porridge, tubers, or unrelated fruit.
6. Similar names and near-identical ingredient sets are duplicate candidates. For example, `香蕉燕麦` and `燕麦香蕉` require review instead of silently becoming two recipes.

## Filter acceptance gate

For every organizer or food filter the user expects:

1. Read the saved recipe and confirm the linked object ID.
2. Query or use the UI filter by that object.
3. Confirm the exact recipe is returned.
4. Clear the filter before testing the next one.

Merely seeing the label on the recipe page does not pass this gate.

## Manual pre-save checklist

When structured audit input cannot be produced, inspect in this order:

- Recipe name and servings.
- Every ingredient row from first through last: quantity, unit, food selector, note.
- Duplicate foods and unintended near matches.
- Every method step against the ingredient list.
- Categories, tags, tools, and their selected objects.
- Expected nutrition and timing fields when the user requested them.

Do not save if any selector still shows a placeholder such as `选择食品`.
