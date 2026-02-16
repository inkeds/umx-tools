# Prompt 配方

## 1) 首轮提问 Prompt

```text
请先不要生成文档，先问我：
1) 是否先生成传统文档（PRD/架构/API/数据库）？
2) 若不先生成传统文档，是否直接进入组合选型并先用 single-file 启动？
```

## 2) traditional-first Prompt

```text
请先生成我指定的传统文档集合，再推荐组合并询问是否以 single-file 生成 Vibe 文档。
```

## 3) direct Prompt

```text
请直接推荐六大组合（主组合+副组合），并提醒我可先用 single-file。
确认后再生成独立保存的 Vibe 文档。
```

## 4) 升级 Prompt

```text
我已有 single-file 文档，请升级到 minimal 多文件，保持 Epic/Story/Spec 一致。
```
