# UMX Tools V3 使用说明

`umx-tools-v3` 是交互式项目文档技能，默认把项目文档保存到**当前路径**。

核心能力：

- 先问路线：`traditional-first` 或 `direct`
- 推荐六大组合（`c1..c6`）
- 支持文档模式：`single-file` / `minimal` / `standard` / `full`
- 文档分离保存：`traditional-docs/` 与 `vibe-docs/`
- Vibe 基座固定：Epic -> Feature/Story -> Spec + 里程碑

## 1. 快速开始（默认当前路径）

建议先创建项目内目录：

```bash
mkdir -p ./umx-inputs ./umx-output
```

### 1.1 先进入交互提问

```bash
bash aiskills/umx-tools-v3/scripts/safe_run_umx_flow.sh \
  aiskills/umx-tools-v3/assets/requirements.example.json \
  ./umx-output \
  ask \
  auto \
  single-file \
  prd,architecture,api,database
```

### 1.2 直接路线（推荐）

```bash
bash aiskills/umx-tools-v3/scripts/safe_run_umx_flow.sh \
  aiskills/umx-tools-v3/assets/requirements.example.json \
  ./umx-output \
  direct \
  auto \
  single-file
```

### 1.3 接受推荐快捷入口

```bash
bash aiskills/umx-tools-v3/scripts/safe_accept_recommend.sh \
  ./umx-inputs/ums-sso-requirements.json \
  ./umx-output
```

## 2. 路线说明

- `traditional-first`：先生成 PRD/架构/API/数据库，再生成 Vibe 文档
- `direct`：直接组合选型后生成 Vibe 文档

## 3. 参数说明

`scripts/safe_run_umx_flow.sh` 参数顺序：

1. requirements.json 路径
2. 输出目录（默认 `./umx-output`）
3. 路线：`ask | traditional-first | direct`
4. 组合：`auto | c1..c6`
5. 模式：`single-file | minimal | standard | full`
6. 传统文档集合：`prd,architecture,api,database`
7. 指令模式（可选）

## 4. 指令模式

```bash
python3 aiskills/umx-tools-v3/scripts/run_umx_flow.py \
  --input ./umx-inputs/ums-sso-requirements.json \
  --output ./umx-output \
  --path ask \
  --command '/umx direct --combo auto --mode single-file'
```

常见指令：

- `/umx start`
- `/umx traditional --docs prd,architecture,api,database --combo auto --mode minimal`
- `/umx direct --combo auto --mode single-file`
- `/umx accept`
- `接受推荐` / `确认` / `接受`

## 5. 输出结构

```text
./umx-output/
  route-summary.md
  traditional-docs/   # 仅 traditional-first 路线
  vibe-docs/
    ...
```

## 6. 为什么会出现前后不一致

常见原因：

1. 没走脚本入口，模型直接写文件。
2. requirements 写入失败后复用了旧文件。

解决方式：

- 只用脚本入口，不手写文件。
- requirements 放到 `./umx-inputs/`，每次确认前先更新。
- 若你必须用 `/tmp`，建议路径固定为 `/tmp/umx-tools-v3/inputs/`。

## 7. fallback 说明

默认输出到当前路径 `./umx-output`。若当前路径不可写，脚本才会自动回退到：

- `/tmp/umx-tools-v3/umx-output`

## 8. Claude Code CLI 对话模板

```text
不要直接写文档文件。
请只执行：
bash aiskills/umx-tools-v3/scripts/safe_accept_recommend.sh ./umx-inputs/ums-sso-requirements.json ./umx-output
执行后只汇报输出目录和文件清单。
```
