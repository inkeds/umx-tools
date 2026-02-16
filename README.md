# umx-tools-v3

一个面向 **Vibe Coding 文档驱动开发** 的通用 Skills 工具。

目标：让用户只给出项目需求，就能在交互中快速选择合适的文档策略（传统文档、AI 文档、或最小单文件模式），并生成可直接用于 AI 开发落地的文档包。

## 核心能力

- 交互优先：先问路线，再生成文档，避免“直接开写导致跑偏”
- 双路线支持：
  - `traditional-first`：先传统文档（PRD/架构/API/数据库）
  - `direct`：直接进入 Vibe 文档（推荐组合 + 模式）
- 六种组合（`c1..c6`）+ 自动推荐（`auto`）
- 四种模式：`single-file` / `minimal` / `standard` / `full`
- Vibe 文档基座固定：`Epic -> Feature/Story -> Spec + Milestone`
- 输出目录扁平：默认两层结构，便于项目集成

## 目录结构

```text
umx-tools-v3/
  SKILL.md
  agents/
  assets/
  references/
  scripts/
  README.md
```

## 快速开始

### 1) 准备输入文件

```bash
mkdir -p ./umx-inputs ./umx-output
cp assets/requirements.template.json ./umx-inputs/requirements.json
```

按你的项目填写 `./umx-inputs/requirements.json`。

### 2) 先走交互入口（推荐）

```bash
bash scripts/safe_run_umx_flow.sh \
  ./umx-inputs/requirements.json \
  ./umx-output \
  ask \
  auto \
  single-file \
  prd,architecture,api,database
```

### 3) 直接接受推荐快速生成

```bash
bash scripts/safe_accept_recommend.sh \
  ./umx-inputs/requirements.json \
  ./umx-output
```

## 常用命令

### 直接路线（MVP 常用）

```bash
bash scripts/safe_run_umx_flow.sh \
  ./umx-inputs/requirements.json \
  ./umx-output \
  direct \
  auto \
  single-file
```

### 传统优先路线

```bash
bash scripts/safe_run_umx_flow.sh \
  ./umx-inputs/requirements.json \
  ./umx-output \
  traditional-first \
  auto \
  minimal \
  prd,architecture,api,database
```

### 指令模式（给 CLI/Agent）

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

## 输出结构（默认）

```text
umx-output/
  route-summary.md
  traditional-docs/      # 仅 traditional-first 路线生成
  vibe-docs/
    ...
```

说明：默认写入当前路径 `./umx-output`。仅当当前路径不可写时，脚本会自动回退到 `/tmp/umx-tools-v3/umx-output`。

## 在 Claude Code CLI 中使用

把本目录放入 Skills 目录后即可调用（目录名建议保持 `umx-tools-v3`）：

```text
~/.claude/skills/umx-tools-v3
```

在对话中建议这样触发：

```text
请使用 umx-tools-v3。
先按交互流程确认路线（traditional-first 或 direct），
再按推荐组合生成文档，默认 single-file 启动。
```

## 设计原则

- 先选择策略，再生成文档
- MVP 优先，避免过度设计
- 文档可扩展：可从 `single-file` 平滑升级到 `minimal/standard/full`
- 传统文档与 Vibe 文档职责分离，便于团队协作与 AI 执行

## 许可证

当前仓库尚未附带 License 文件。建议开源前补充 `LICENSE`（常见：MIT/Apache-2.0）。
