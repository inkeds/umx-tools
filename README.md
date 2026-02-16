# umx-tools-v3

`umx-tools-v3` 是一套面向 **Claude Code / 各类 AI CLI** 的通用 Skills 工具，目标是：
**用户只需描述项目需求，即可通过交互选型，快速生成可执行的项目文档包**。

核心定位：
- 优先用于 CLI 场景（尤其 Claude Code）
- 同时支持传统文档驱动与 Vibe Coding 文件驱动
- 默认从最小文档启动，避免 MVP 过度设计

## 1. 在 Claude Code CLI 中使用（优先看这里）

### 1.1 安装到 Skills 目录

```bash
mkdir -p ~/.claude/skills
cp -r ./umx-tools-v3 ~/.claude/skills/umx-tools-v3
```

### 1.2 在对话里触发技能

可直接对 Claude 说：

```text
请使用 umx-tools-v3：
先按交互流程确认是 traditional-first 还是 direct，
再推荐组合与模式，默认 single-file 启动，最后生成文档包。
```

### 1.3 推荐对话节奏

- 第一步：先确定路线
  - `traditional-first`（先 PRD/架构/API/数据库）
  - `direct`（直接 Vibe 文档）
- 第二步：选择组合（`auto` 或 `c1..c6`）
- 第三步：选择模式（`single-file|minimal|standard|full`）
- 第四步：生成输出到 `./umx-output`

## 2. 项目介绍：两条路线 + 一个文档基座

无论走哪条路线，Vibe 文档始终使用统一基座：

`Epic -> Feature/Story -> Spec + Milestone`

### 2.1 路线 A：traditional-first

适合先对齐团队共识或对外协作：
- 先产出传统文档：PRD / 架构 / API / 数据库
- 再进入 Vibe 文档生成

### 2.2 路线 B：direct

适合个人开发或 MVP 快速验证：
- 直接进入组合选型
- 优先 `single-file` 或 `minimal`
- 快速拿到可执行文档包

## 3. 六种组合方式（c1..c6）

| 组合 | 核心流程 | 适合场景 | 推荐起步模式 |
|---|---|---|---|
| `c1` | 需求画布 -> 原型 -> AI 生成 | 小工具、快速起盘 | `single-file` |
| `c2` | Story Mapping -> 任务拆解 -> AI 迭代 | 中小项目持续迭代 | `minimal` |
| `c3` | 场景驱动 -> 接口定义 -> 前后端并行 | 前后端分离、联调优先 | `minimal` |
| `c4` | Figma -> Prompt -> AI 全栈 | 设计驱动产品 | `standard` |
| `c5` | 精益 MVP -> 反馈 -> AI 快迭代 | 0 到 1 验证、快速试错 | `single-file` |
| `c6` | DDD 精简 -> 骨架 -> AI 填充 | 复杂业务、长期治理 | `standard` / `full` |

默认推荐：
- `auto + single-file`（先跑通最小闭环）
- 有明确接口协作需求时优先 `c3`
- 复杂领域建模需求时优先 `c6`

## 4. 文档模式说明

- `single-file`：单文件最小启动，适合 MVP
- `minimal`：最小多文件闭环，适合小团队
- `standard`：标准协作包，适合跨角色协作
- `full`：治理增强包，适合中长期演进

## 5. 脚本用法（本地/CI/Agent）

### 5.1 准备输入

```bash
mkdir -p ./umx-inputs ./umx-output
cp assets/requirements.template.json ./umx-inputs/requirements.json
```

填写 `./umx-inputs/requirements.json` 后执行。

### 5.2 交互入口（推荐）

```bash
bash scripts/safe_run_umx_flow.sh \
  ./umx-inputs/requirements.json \
  ./umx-output \
  ask \
  auto \
  single-file \
  prd,architecture,api,database
```

### 5.3 直接接受推荐

```bash
bash scripts/safe_accept_recommend.sh \
  ./umx-inputs/requirements.json \
  ./umx-output
```

### 5.4 指令模式

```bash
python3 scripts/run_umx_flow.py \
  --input ./umx-inputs/requirements.json \
  --output ./umx-output \
  --path ask \
  --command '/umx direct --combo auto --mode single-file'
```

支持指令：
- `/umx start`
- `/umx traditional --docs prd,architecture,api,database --combo auto --mode minimal`
- `/umx direct --combo auto --mode single-file`
- `/umx accept`
- `接受推荐` / `确认` / `开始生成`

## 6. 输出结构（默认两层）

```text
umx-output/
  route-summary.md
  traditional-docs/      # 仅 traditional-first 生成
  vibe-docs/
    ...
```

默认输出到当前路径 `./umx-output`；仅当前路径不可写时，自动回退到 `/tmp/umx-tools-v3/umx-output`。

## 7. 仓库结构

```text
umx-tools-v3/
  SKILL.md
  agents/
  assets/
  references/
  scripts/
  README.md
  LICENSE
```

## 8. License

本项目采用 MIT License。详见 `LICENSE`。
