# Mealie Agent Toolkit

[English](README.md)

[![CI](https://github.com/alanthssss/mealie-agent-toolkit/actions/workflows/ci.yml/badge.svg)](https://github.com/alanthssss/mealie-agent-toolkit/actions/workflows/ci.yml)
[![MIT license](https://img.shields.io/badge/license-MIT-8ee3c1.svg)](LICENSE)
[![Agent Skills](https://img.shields.io/badge/Agent%20Skills-compatible-ff715b.svg)](https://agentskills.io/specification)

![结构化食谱通过确定性质量门禁](docs/assets/hero.png)

**[项目网站](https://alanthssss.github.io/mealie-agent-toolkit/) · [真实 Mealie 示例](docs/demo/tomato-eggs.md) · [反馈失败案例](https://github.com/alanthssss/mealie-agent-toolkit/issues/new/choose)**

这是一个兼容开放 Agent Skills 规范的 Mealie 质量控制层，用于安全地创建、更新和审查食谱、周/月餐单、筛选关联与购物数据。

核心不是“替 Agent 点网页”，而是把容易遗漏的检查变成保存前、保存后的强制门禁：

- 食材必须关联正确的食品对象，不能只填显示文字。
- 按预期名称和稳定 ID 核对，阻止 `水` 被选成 `水芹`、`鸡蛋` 被选成 `鸡蛋果`。
- 数量、单位、食品和备注各司其职，避免显示成 `500克 500克 红薯`。
- 检查食材和做法是否互相对应。
- 检测 `燕麦香蕉` / `香蕉燕麦` 一类重复候选。
- 分开核算用餐次数、总份数和唯一食谱数。
- 保存后重新读取，并实际验证分类、标签、用具和食品筛选。

## 真实示例

我们用本 Skill 检查了本地 Mealie 3.25.1 中一份看起来完整的“番茄炒蛋（示范）”。编辑页暴露出五项食材其实都是“数量 0、单位空、食品空、整句写在备注”，所以精确 `番茄` 筛选找不到它。

修复过程在每次保存前逐行核对，选择规范食品 `番茄`，把 `西红柿` 设为别名，补齐 `家常菜`、`快手菜`、`炒锅`，保存后读回，再分别执行精确 `番茄` 和 `鸡蛋` 筛选。两项均命中，`树番茄`、`鸡蛋果` 等近似项均未选中。[查看完整证据记录](docs/demo/tomato-eggs.md)。

## 安装

```bash
mkdir -p ~/.agents/skills
ln -s "$(pwd)/skills/mealie-quality-operator" ~/.agents/skills/mealie-quality-operator
```

## 审计

```bash
python3 skills/mealie-quality-operator/scripts/audit_mealie.py recipe recipe.json \
  --policy skills/mealie-quality-operator/assets/policy.example.json \
  --strict
```

退出码 `0` 表示通过；`1` 表示存在错误，或者严格模式下存在警告；`2` 表示输入或调用方式错误。

当前仓库提供跨版本 Skill 和审计器。实际 Mealie 连接器应读取目标实例的 `/openapi.json`，再将返回数据归一化为 `references/audit-schema.md` 描述的结构。不要将令牌、Cookie、内网地址或私人食谱提交到仓库。

## 项目状态与参与方式

这是一个早期但可用的版本。当前已有 Skill、策略、审计结构、测试夹具和确定性 CLI；后续重点包括 REST/MCP 适配器、匿名失败案例和更多语言别名。欢迎查看 [贡献指南](CONTRIBUTING.md) 与 [路线图](ROADMAP.md)。如果它确实帮你避免了一次错误，Star 或提交一条真实案例 Issue 都会让更多自托管用户发现并完善它。
