---
name: umx-tools-v3
description: 交互式项目文档技能。用户先给需求，技能先询问是否先走传统文档（PRD/架构/API/数据库）；若选择传统优先，先生成传统文档；若选择直接开始，先推荐并确认六大组合方式，并提醒可先用单文件最小模式。确认后生成独立保存的 AI Vibe Coding 文件驱动文档（Epic -> Spec + 里程碑），用于降低新手 AI 编程中的幻觉、上下文丢失与 Bug 循环。支持命令模式进入同一流程。
---

# UMX Tools V3

按以下顺序执行，默认直接落地，不做空泛讨论。

## 0) Claude Code CLI 硬规则（必须遵守）

1. 不要直接用写文件工具逐个写文档。
2. 一律通过脚本生成文档：`safe_run_umx_flow.sh` 或 `safe_accept_recommend.sh`。
3. 若用户说“接受推荐/开始生成”，直接走：`direct + auto + single-file`。
4. 使用 `safe_accept_recommend.sh`，启用输入文件旧版本保护，避免复用旧 requirements。
5. 若 requirements 写入失败，不要继续生成，先让用户重新提供 requirements 文件路径。
6. 默认输出到当前项目路径（`./umx-output`），仅在不可写时回退到 `/tmp/umx-tools-v3/umx-output`。
7. 生成前必须通过输入质量闸门：`project_name/project_goal/target_users` 不能是占位文本；仅草稿场景才允许 `--allow-placeholder`。

## 1) 执行边界

1. 不修改用户原有业务代码。
2. 传统文档与 Vibe 文档必须分目录保存。
3. Vibe 文档必须符合 Epic -> Feature/Story -> Spec + 里程碑。

## 2) 首轮交互（必须先问）

收到需求后，先问：

1. 是否先从传统项目文档开始？（PRD/架构/API/数据库）
2. 若是，具体需要哪些传统文档？
3. 若否，是否直接进入组合选型并生成 Vibe 文档？

若用户回答不完整，只补问必要字段，不跳过这一步。

流程详情见：`references/interaction-flow.md`

## 3) 路线分支

### A. traditional-first

1. 先生成 `traditional-docs/`。
2. 再推荐组合（主组合+副组合）并提示可先用 `single-file`。
3. 用户确认后生成 `vibe-docs/`。

### B. direct

1. 基于需求推荐组合并让用户确认。
2. 提醒优先 `single-file` 或 `minimal` 起步。
3. 生成 `vibe-docs/`。

## 4) 文档模式

- `single-file`: 单文件快速启动
- `minimal`: 多文件最小闭环
- `standard`: 协作迭代
- `full`: 治理与规模化

模式说明见：`references/min-doc-modes.md`

## 5) 脚本入口

优先使用流程脚本：

```bash
bash <skill-dir>/scripts/safe_run_umx_flow.sh \
  <requirements.json> \
  ./umx-output \
  ask \
  auto \
  single-file \
  prd,architecture,api,database
```

“接受推荐”快捷入口：

```bash
bash <skill-dir>/scripts/safe_accept_recommend.sh \
  <requirements.json> \
  ./umx-output
```

参数：

- 第 3 位：`ask|traditional-first|direct`
- 第 4 位：`auto|c1..c6`
- 第 5 位：`single-file|minimal|standard|full`
- 第 6 位：传统文档集合
- 环境变量：`UMX_ALLOW_PLACEHOLDER=1`（仅草稿预演时允许占位输入）

## 6) 指令模式（Command Mode）

支持：

- `/umx start`
- `/umx traditional --docs prd,architecture,api,database --combo auto --mode minimal`
- `/umx direct --combo auto --mode single-file`
- `/umx accept`
- 自然语言快捷词：`接受推荐`、`确认方案`、`开始生成`

规则见：`references/command-mode.md`

## 7) 输出约定

最终回复用户时必须包含：

- 路线：traditional-first 或 direct
- 组合结果：主组合 + 副组合
- 模式：single-file/minimal/standard/full
- 输出路径固定为：`./umx-output/traditional-docs/` 与 `./umx-output/vibe-docs/`
- 执行护栏固定包含：范围边界、单一事实源、变更先回文档
- 下一步建议：先从哪份文档开始执行
