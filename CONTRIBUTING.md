# Contributing

Contributions should turn demonstrated Mealie failure modes into narrow, reusable rules rather than accumulating generic prompt advice.

1. Open an issue describing the observable failure, Mealie version, transport path, and expected invariant. Remove private recipes, tokens, hostnames, and household identifiers.
2. Add or update a fixture or unit test that fails before the change.
3. Prefer deterministic validation in `audit_mealie.py` when the invariant can be evaluated from data. Keep judgment-heavy workflow guidance in `SKILL.md` or a focused reference.
4. Run `python3 -m unittest discover -s tests -v` and both CLI fixtures before submitting.
5. Do not add destructive automation without exact-ID resolution, an impact preview, and an explicit approval boundary.

Transport-specific adapters should normalize their payloads to `references/audit-schema.md` and remain isolated from core quality policy.
