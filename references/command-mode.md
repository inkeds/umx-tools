# 指令模式

## 命令示例

- `/umx start`
- `/umx traditional --docs prd,architecture,api,database --combo auto --mode minimal`
- `/umx direct --combo c2 --mode single-file`
- `/umx recommend --mode single-file`
- `/umx accept`

## 自然语言快捷词

以下输入等价于“接受推荐并开始生成”：

- `接受推荐`
- `确认`
- `接受`
- `确认推荐`
- `确认方案`
- `开始生成`
- `开始生成文档`

默认映射：`direct + auto + single-file`。

## 映射规则

- `start` -> 进入首轮提问，不落盘。
- `traditional` -> 走 traditional-first 路线。
- `direct` -> 走 direct 路线。
- `recommend` -> 仅输出组合推荐，不写文件。
- `accept`/快捷词 -> 直接生成 single-file（推荐路径）。

## Claude Code CLI 注意

- 不要直接让模型逐个写文档文件。
- 必须调用脚本落盘，否则容易触发 `Error writing file` 循环。

## 输入质量闸门

- 生成前会校验 `project_name/project_goal/target_users`，占位文本会被拒绝。
- 仅草稿预演可临时放开：`UMX_ALLOW_PLACEHOLDER=1`。
