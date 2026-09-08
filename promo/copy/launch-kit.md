# Mealie Agent Toolkit launch kit

Canonical URL: https://github.com/alanthssss/mealie-agent-toolkit
Live site: https://alanthssss.github.io/mealie-agent-toolkit/

## GitHub release

**Title:** v0.1.0 — deterministic quality gates for Mealie agents

Mealie Agent Toolkit turns recurring recipe-automation failures into explicit pre-save and post-save checks. The first release includes an Agent Skills-compatible workflow, a dependency-free Python auditor, policy and schema references, regression fixtures, and a documented real Mealie 3.25.1 repair.

It catches empty food links hidden behind display text, wrong fuzzy matches such as 水 → 水芹 and 鸡蛋 → 鸡蛋果, duplicated display fields, ingredient/method drift, duplicate recipes, plan-count confusion, and missing filter relationships.

## Show HN

**Title:** Show HN: Quality gates for agents that write to Mealie

I kept seeing recipe forms look correct while the underlying food relationship was empty or wrong. A label saying “water” is not proof that the selected catalog object is water, and a saved recipe is not proof that filters or shopping aggregation work.

I turned those failures into an open Agent Skill plus a dependency-free Python auditor. It checks structured ingredient rows, intended food identity, method coverage, duplicates, plan arithmetic, and defines a read-after-write/filter contract for live adapters. I also documented a real local Mealie repair where all five visible ingredients were actually unlinked.

I would especially value feedback from Mealie users and people building agents against self-hosted apps.

## Reddit — r/selfhosted / r/opensource

**Title:** I open-sourced the quality gates I use before an agent saves Mealie recipes

I learned the annoying way that a Mealie recipe can *look* complete while quantity/unit/food relationships are empty. Fuzzy selection can also turn short names into the wrong catalog object, which later breaks filters and shopping lists.

This repo packages the checks as an Agent Skills-compatible workflow and a local Python CLI. No runtime dependencies or telemetry. The README includes a real repair and exact filter regression test. It is early, so failure cases and adapter contributions are welcome.

Disclosure: independent community project; not affiliated with Mealie.

## X / Twitter thread

1. A recipe form can look correct while its data is broken. “2 tomatoes” may actually be quantity=0, unit=null, food=null, with the whole phrase stuffed into a note.
2. That is how filters fail, shopping quantities split, and fuzzy matches turn 水 into 水芹 or 鸡蛋 into 鸡蛋果.
3. I open-sourced Mealie Agent Toolkit: deterministic pre-save gates + read-after-write verification for agents that create recipes and meal plans.
4. It is Agent Skills-compatible, MIT licensed, dependency-free at runtime, and includes a real Mealie 3.25.1 repair. [GitHub URL]

## LinkedIn

The dangerous automation bug is often not a crash. It is a form that looks correct while the underlying relationships are empty.

Mealie Agent Toolkit converts the failure cases we found while automating structured recipes into reusable quality gates: exact food identity, structured field separation, method coverage, duplicate detection, plan arithmetic, and read-after-write filter tests.

The first open-source release includes an Agent Skill, a dependency-free Python auditor, tests, and a documented real-world repair. Feedback from self-hosters and agent builders is welcome.

## V2EX / 即刻 / 少数派

**标题：** 我把 Agent 录入 Mealie 时踩过的坑，做成了一个开源质量门禁 Skill

自动录食谱最麻烦的不是“没保存”，而是“看着保存好了，底层数据却是错的”：食材整句被塞进备注，食品关联为空；`水` 模糊匹配成 `水芹`；`鸡蛋` 多出 `鸡蛋果`；两份牛奶不聚合；食材和做法对不上；30 天餐单的餐次、份数、唯一食谱数还容易混算。

我把这些真实问题整理成 Mealie Agent Toolkit：开放 Agent Skills 兼容的操作流程 + 无运行依赖的 Python 审计器。保存前逐行检查，保存后重新读取，并真的跑分类、标签、用具和食品筛选。仓库里还有一次 Mealie 3.25.1 的完整修复记录。

目前是早期可用版，欢迎贡献匿名失败案例、别名表和 REST/MCP 适配器。项目与 Mealie 官方无隶属关系。

## Short video caption

Your recipe looks complete. Its food links may still be empty. Mealie Agent Toolkit adds deterministic quality gates before Save—and verifies the exact filters after. Open source, MIT, Agent Skills-compatible. #selfhosted #opensource #aiagents #mealie

## Publishing checklist

- Use the square image for feed posts and the vertical MP4 for short-video platforms.
- Lead with the concrete hidden-data failure, not generic “AI productivity.”
- Link directly to the repository or live demo.
- State that the project is early and independent from Mealie.
- Reply with technical detail; do not buy stars, mass-post, or ask for empty engagement.
- Stagger launches and incorporate feedback between communities rather than duplicating the same post everywhere.
