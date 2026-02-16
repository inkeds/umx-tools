# 交互流程

## 总流程

1. 用户提出项目需求。
2. 先确认路线：`traditional-first` 或 `direct`。
3. 若 `traditional-first`：先生成传统文档，再进入组合确认。
4. 若 `direct`：直接推荐组合并确认。
5. 提醒用户可先用 `single-file` 启动。
6. 确认后生成独立保存的 Vibe 文档。

## 首轮必问

1. 是否先生成传统文档？
2. 需要哪些传统文档（PRD/架构/API/数据库）？
3. 是否接受自动推荐组合？
4. 是否先用 single-file 模式？

## 独立保存要求

- 传统文档：`traditional-docs/`
- Vibe 文档：`vibe-docs/`

Vibe 文档必须包含 Epic -> Feature/Story -> Spec + 里程碑。
