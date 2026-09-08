# Mealie integration contract

Keep transport details outside the skill's business rules. An adapter may be an MCP server, REST client, or browser driver, but it must expose equivalent observable behavior.

## Capability boundary

The adapter should support:

- Read instance version and live OpenAPI document.
- Search and fetch foods, units, categories, tags, and tools with stable IDs.
- Read, create, and update recipes.
- Read and reconcile meal-plan entries and shopping lists.
- Query recipes using the same filters available to users.

The skill owns intent interpretation, canonicalization policy, quality gates, retry limits, and completion evidence. The adapter owns authentication, HTTP/UI mechanics, pagination, version-specific schemas, and typed error reporting.

## Version strategy

1. Fetch `/openapi.json` from the target instance at session start or from a short-lived cache.
2. Select operations by `operationId` or verified path and HTTP method; do not assume paths from another Mealie version.
3. Translate instance payloads into [the audit schema](audit-schema.md) at the adapter boundary and attach user-intent expectations before the pre-save audit.
4. Preserve unknown response fields during read-modify-write operations when the API requires full objects.
5. Never commit base URLs, tokens, cookies, household IDs, or exported private recipes to the open-source repository.

## Required mutation semantics

Every write command should support a dry-run representation and return:

- Operation and exact target identity.
- Before/after or proposed payload summary.
- Server response identity and revision/timestamp when available.
- A freshly fetched object for post-save audit.

Merge and delete operations must resolve exact IDs, enumerate affected references, and require explicit confirmation immediately before execution.

## Browser fallback

Browser control is a compatibility fallback, not the data model. Before Save, scan every row and visible selector. After Save, reopen the record rather than trusting a toast notification. For selectors, distinguish typed text from a selected object and validate through the corresponding filter.
