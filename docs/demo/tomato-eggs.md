# Real demo: repairing a filter-broken recipe

Tested on a private local Mealie 3.25.1 instance on 2026-09-08. No private URL, token, cookie, household identifier, or catalog ID is stored here.

## What looked correct

The read view showed `2 个 西红柿`, `3 个 鸡蛋`, oil, salt, sugar, and five relevant cooking steps.

## What the editor revealed

All five ingredient rows were unstructured: `quantity = 0`, unit empty, food empty, and the full rendered phrase stored in the note. Consequently, selecting the exact canonical food filter `番茄` returned five other recipes but not `番茄炒蛋（示范）`.

## Skill-driven repair

1. Captured the intended food for every row before selection.
2. Used Mealie's parser, then reviewed every proposed quantity, unit, food, and note.
3. Rejected a new standalone `西红柿` catalog object; selected exact canonical `番茄` and added `西红柿` as its alias.
4. Confirmed all five rows before the outer recipe save: `2 个 番茄`, `3 个 鸡蛋`, `1 汤匙 食用油`, `0.5 茶匙 盐`, `1 茶匙 白糖`.
5. Added filterable metadata: category `家常菜`, tag `快手菜`, tool `炒锅`.
6. Saved once, re-read the recipe, and compared all fields.
7. Executed exact food filters. Both `番茄` and `鸡蛋` returned the recipe. `树番茄`, `鸡蛋果`, and `鸡蛋果鸡蛋` remained unselected.

## Reproducible offline audit

```bash
python3 skills/mealie-quality-operator/scripts/audit_mealie.py \
  recipe examples/local-demo/tomato-eggs-corrected.json --strict
```

The pre-repair transcription and normalized draft are kept in [`examples/local-demo`](../../examples/local-demo/). Browser observations are summarized rather than exported so private instance data cannot leak into the repository.

## Gate result

| Gate | Result |
| --- | --- |
| Recipe identity | PASS |
| Structured ingredient completeness | PASS — 5/5 |
| Expected vs selected foods | PASS — 5/5 |
| Ingredient ↔ method coverage | PASS |
| Category / tag / tool links | PASS |
| Read-after-write comparison | PASS |
| Exact `番茄` filter | PASS |
| Exact `鸡蛋` filter | PASS |
