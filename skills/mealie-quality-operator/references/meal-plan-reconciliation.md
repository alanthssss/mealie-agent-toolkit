# Meal-plan reconciliation

Do not use `number of recipes`, `meal occurrences`, and `servings` interchangeably.

## Definitions

- **Unique recipe:** one canonical recipe record, regardless of how often it is scheduled.
- **Meal occurrence:** one planned breakfast, lunch, dinner, or snack slot.
- **Serving:** one person's portion in an occurrence.

For 30 days, three meal slots per day, and two people:

- Expected meal occurrences: `30 × 3 = 90`.
- Expected servings: `90 × 2 = 180`.
- Unique recipes: a design choice based on desired variety, not automatically 90 or 21.

## Reconciliation sequence

1. Establish days, slots per day, people, and any skipped meals.
2. Count scheduled entries by date and slot.
3. Resolve every entry to an exact recipe ID.
4. Compare entry servings with recipe yield and scaling behavior.
5. Count unique recipe IDs separately.
6. Aggregate shopping quantities only after units and canonical foods are linked.
7. Report unit conflicts instead of adding unlike units blindly.

## Duplicate review

Treat recipes as duplicate candidates when they have highly overlapping canonical food sets and equivalent purposes, even if the title word order differs. Do not automatically delete or merge them: present the IDs and evidence, then ask for authorization before destructive cleanup.

## Completion report

Include:

- Planned versus actual occurrences.
- Planned versus actual servings.
- Unique recipes and reuse count.
- Missing recipe links.
- Duplicate candidates.
- Foods or units that could not be aggregated safely.
