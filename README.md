# Mealie Agent Toolkit

[简体中文](README.zh-CN.md)

[![CI](https://github.com/alanthssss/mealie-agent-toolkit/actions/workflows/ci.yml/badge.svg)](https://github.com/alanthssss/mealie-agent-toolkit/actions/workflows/ci.yml)
[![MIT license](https://img.shields.io/badge/license-MIT-8ee3c1.svg)](LICENSE)
[![Agent Skills](https://img.shields.io/badge/Agent%20Skills-compatible-ff715b.svg)](https://agentskills.io/specification)

![Structured recipes passing through deterministic quality gates](docs/assets/hero.png)

**[Live site](https://alanthssss.github.io/mealie-agent-toolkit/) · [Real Mealie demo](docs/demo/tomato-eggs.md) · [Report a failure case](https://github.com/alanthssss/mealie-agent-toolkit/issues/new/choose)**

An open Agent Skills-compatible quality layer for creating and auditing structured [Mealie](https://mealie.io/) data.

The first included skill, `mealie-quality-operator`, captures practical safeguards for recipe entry, meal planning, filters, and shopping aggregation. It is intentionally transport-neutral: use it with a Mealie MCP server, the live REST/OpenAPI interface, or an authenticated browser.

## Why this exists

Recipe forms can look complete while their underlying relationships are empty or wrong. A typed ingredient label is not necessarily a linked food; fuzzy search can select `水芹` for `水`; copied display strings can render duplicated quantities; generic methods can disagree with ingredients; and reordered names can create duplicate recipes.

This toolkit turns those failure modes into explicit pre-save and post-save gates.

## What it catches

| Failure | Gate |
| --- | --- |
| `水` linked to `水芹`; `鸡蛋` linked to `鸡蛋果` | Intended name/ID must match the selected food object |
| `500克 500克 红薯` | Quantity, unit, food, and note are audited separately |
| Ingredient list and method disagree | Ingredient-to-instruction coverage check |
| `燕麦香蕉` and `香蕉燕麦` become duplicates | Canonical ingredient-set overlap detection |
| 30 days × 3 meals confused with 21 recipes | Occurrences, servings, and unique recipes reported separately |
| A saved recipe disappears from filters | Read-after-write plus live filter verification contract |

## Real-world proof

We used the skill against a local Mealie 3.25.1 recipe that looked complete but had **five empty food links**. The workflow repaired every structured row, mapped `西红柿` to canonical `番茄`, added category/tag/tool metadata, re-read the saved record, and verified exact `番茄` and `鸡蛋` filters. [Read the evidence log](docs/demo/tomato-eggs.md).

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

## Project status

This is an early, working release: the transport-neutral skill, policy, schema, fixtures, and deterministic CLI are usable today. Contributions for Mealie REST/MCP adapters, anonymized failure fixtures, and additional language aliases are especially welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) and the [roadmap](ROADMAP.md).

If this solves a real failure in your setup, a GitHub star and a short issue describing the case help other self-hosters discover and improve it. No telemetry is collected.

## Security

Do not commit API tokens, cookies, private recipe exports, LAN addresses, or household identifiers. Treat third-party skills as privileged instructions and code; review them before installation. Destructive operations such as recipe deletion or food merging are deliberately outside the bundled auditor and require explicit authorization in an adapter.

## License

MIT
