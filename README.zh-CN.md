# Mealie Agent Toolkit

这是一个兼容开放 Agent Skills 规范的 Mealie 质量控制层，用于安全地创建、更新和审查食谱、周/月餐单、筛选关联与购物数据。

核心不是“替 Agent 点网页”，而是把容易遗漏的检查变成保存前、保存后的强制门禁：

- 食材必须关联正确的食品对象，不能只填显示文字。
- 按预期名称和稳定 ID 核对，阻止 `水` 被选成 `水芹`、`鸡蛋` 被选成 `鸡蛋果`。
- 数量、单位、食品和备注各司其职，避免显示成 `500克 500克 红薯`。
- 检查食材和做法是否互相对应。
- 检测 `燕麦香蕉` / `香蕉燕麦` 一类重复候选。
- 分开核算用餐次数、总份数和唯一食谱数。
- 保存后重新读取，并实际验证分类、标签、用具和食品筛选。

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
