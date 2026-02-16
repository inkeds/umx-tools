# 故障排查

## 症状：`Error writing file` 循环

典型日志：

- 已执行 `mkdir -p ...`
- 随后连续出现 `Error writing file`
- 模型持续重试写文件

## 根因

1. 模型直接逐个写文档，没有调用脚本。
2. requirements 写入失败，后续复用了旧文件。

## 推荐修复（当前路径）

```bash
mkdir -p ./umx-inputs ./umx-output
bash <skill-dir>/scripts/safe_accept_recommend.sh \
  ./umx-inputs/ums-sso-requirements.json \
  ./umx-output
```

## /tmp 仅作为兜底

如果当前路径不可写，再使用：

```bash
bash <skill-dir>/scripts/safe_accept_recommend.sh \
  /tmp/umx-tools-v3/inputs/ums-sso-requirements.json \
  /tmp/umx-tools-v3/umx-output
```

## 关于旧文件保护

`safe_accept_recommend.sh` 默认会拒绝过旧的 `/tmp` 输入文件（默认超过 600 秒）。

- 修改阈值：`UMX_MAX_INPUT_AGE_SECONDS=1800`
- 允许旧文件：`UMX_ALLOW_STALE_INPUT=1`

## 关于输入质量闸门

`generate_doc_pack.py` 默认会校验关键字段（项目名称/目标/目标用户）是否仍是占位文本。

- 若提示 `Input quality check failed`：请先补全 `requirements.json`。
- 仅草稿预演可使用：`UMX_ALLOW_PLACEHOLDER=1`（或底层参数 `--allow-placeholder`）。


## 结果校验

- `route-summary.md` 存在
- `vibe-docs/` 存在
- `single-file` 模式下存在 `00-single-file-pack.md`
