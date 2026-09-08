# Mealie Agent Toolkit

[简体中文](README.zh-CN.md)

An open Agent Skills-compatible quality layer for creating and auditing structured [Mealie](https://mealie.io/) data.

The first included skill, `mealie-quality-operator`, captures practical safeguards for recipe entry, meal planning, filters, and shopping aggregation. It is intentionally transport-neutral: use it with a Mealie MCP server, the live REST/OpenAPI interface, or an authenticated browser.

## Why this exists

Recipe forms can look complete while their underlying relationships are empty or wrong. A typed ingredient label is not necessarily a linked food; fuzzy search can select `水芹` for `水`; copied display strings can render duplicated quantities; generic methods can disagree with ingredients; and reordered names can create duplicate recipes.

This toolkit turns those failure modes into explicit pre-save and post-save gates.

## Install the skill

Copy or symlink the skill directory into a supported skills location:

```bash
mkdir -p ~/.agents/skills
ln -s "$(pwd)/skills/mealie-quality-operator" ~/.agents/skills/mealie-quality-operator
```

Compatible agents may also load the repository's `skills/` directory directly. The skill follows the open [Agent Skills specification](https://agentskills.io/specification).

For portability, its frontmatter uses the common subset accepted by both the open specification and Codex's current validator. Environment requirements live in the instruction body rather than the optional specification-level `compatibility` field.

## Audit JSON

The auditor accepts Mealie-like recipe JSON and common export variants:

```bash
python3 skills/mealie-quality-operator/scripts/audit_mealie.py recipe recipe.json \
  --policy skills/mealie-quality-operator/assets/policy.example.json \
  --strict

python3 skills/mealie-quality-operator/scripts/audit_mealie.py collection recipes.json --strict
```

Exit code `0` passes. Exit code `1` means errors exist, or warnings exist under `--strict`. Use `--format json` for automation.

## Development

```bash
python3 -m pip install -r requirements-dev.txt
python3 -m unittest discover -s tests -v
python3 /path/to/skill-creator/scripts/quick_validate.py \
  skills/mealie-quality-operator
```

The project has no runtime dependencies beyond Python 3.10+.

## Security

Do not commit API tokens, cookies, private recipe exports, LAN addresses, or household identifiers. Treat third-party skills as privileged instructions and code; review them before installation. Destructive operations such as recipe deletion or food merging are deliberately outside the bundled auditor and require explicit authorization in an adapter.

## License

MIT
