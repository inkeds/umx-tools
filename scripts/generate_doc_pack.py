#!/usr/bin/env python3
"""Generate an executable project doc pack from a requirements JSON.

The pack always uses Epic -> Feature/Story -> Core Spec as baseline,
then appends one of six combo extensions and optional doc layers.
Supports single-file mode for all-in-one output.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

LEVEL_MAP = {"low": 0, "medium": 1, "high": 2}
SPEED_MAP = {"slow": 0, "normal": 1, "fast": 2}
DESIGN_VALUES = {"none", "wireframe", "figma"}
MODE_VALUES = {"minimal", "standard", "full", "single-file"}
MODE_ALIAS = {"single": "single-file", "single_file": "single-file", "single-file": "single-file"}
COMBO_VALUES = {"c1", "c2", "c3", "c4", "c5", "c6"}


@dataclass(frozen=True)
class Combo:
    code: str
    name: str
    pipeline: str
    fit: str


COMBOS = {
    "c1": Combo("c1", "需求画布驱动", "需求画布 -> 原型 -> AI 生成", "个人工具、轻量项目、快速起步"),
    "c2": Combo("c2", "Story Mapping 驱动", "Story Mapping -> 任务拆解 -> AI 迭代", "中小项目、持续迭代、多人协作"),
    "c3": Combo("c3", "场景与契约驱动", "场景驱动(SDD) -> 接口定义 -> 前后端并行", "前后端分离、接口协作、联调成本高"),
    "c4": Combo("c4", "设计驱动", "Figma -> Prompt -> AI 全栈", "UI/交互导向项目、设计优先"),
    "c5": Combo("c5", "精益 MVP 驱动", "精益 MVP -> 反馈 -> AI 快迭代", "想法验证、快速试错"),
    "c6": Combo("c6", "DDD 精简驱动", "DDD 精简 -> 骨架 -> AI 填充", "复杂领域、团队交付、长期维护"),
}

BASELINE_DOCS = [
    ("00-epic-map.md", "Epic Map"),
    ("01-feature-story-map.md", "Feature Story Map"),
    ("02-core-spec.md", "Core Spec"),
]

BASE_DOCS = [
    ("03-combo-decision.md", "组合决策记录"),
    ("04-milestone-plan.md", "里程碑计划"),
    ("05-ai-prompt-pack.md", "AI 执行 Prompt 包"),
]

COMBO_MIN_DOCS: Dict[str, List[Tuple[str, str]]] = {
    "c1": [
        ("30-requirement-canvas.md", "需求画布"),
        ("31-prototype-brief.md", "原型说明"),
    ],
    "c2": [
        ("30-iteration-slice.md", "迭代切片计划"),
        ("31-iteration-backlog.md", "迭代任务清单"),
    ],
    "c3": [
        ("30-scenario-list.md", "场景清单"),
        ("31-api-contract-priority.md", "接口契约优先级"),
        ("32-data-model.md", "数据模型"),
    ],
    "c4": [
        ("30-ui-flow-map.md", "UI 流程与设计约束"),
        ("31-figma-to-prompt-map.md", "Figma 到 Prompt 映射"),
    ],
    "c5": [
        ("30-mvp-hypothesis.md", "MVP 假设"),
        ("31-feedback-loop.md", "反馈闭环"),
    ],
    "c6": [
        ("30-domain-map.md", "领域拆分"),
        ("31-ubiquitous-language.md", "统一语言"),
        ("32-service-boundary.md", "应用服务边界"),
    ],
}

STANDARD_DOCS = [
    ("10-prd-lite.md", "PRD Lite"),
    ("11-architecture-lite.md", "Architecture Lite"),
    ("12-api-spec.md", "API Spec"),
    ("13-database-design.md", "Database Design"),
    ("14-risk-checklist.md", "风险与回归清单"),
]

FULL_DOCS = [
    ("20-module-spec-index.md", "模块 Spec 索引"),
    ("21-test-regression-plan.md", "测试与回归计划"),
    ("22-ops-runbook.md", "运维 Runbook"),
    ("23-change-log-governance.md", "变更治理"),
]

SINGLE_FILE_DOC = ("00-single-file-pack.md", "单文件项目文档包")


def to_int(value: object, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def normalize_level(value: object, default: str) -> str:
    text = str(value).strip().lower() if value is not None else default
    return text if text in LEVEL_MAP else default


def normalize_speed(value: object, default: str = "normal") -> str:
    text = str(value).strip().lower() if value is not None else default
    return text if text in SPEED_MAP else default


def normalize_design(value: object, default: str = "none") -> str:
    text = str(value).strip().lower() if value is not None else default
    return text if text in DESIGN_VALUES else default


def normalize_bool(value: object, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in {"true", "1", "yes", "y"}:
            return True
        if lowered in {"false", "0", "no", "n"}:
            return False
    return default


def normalize_mode_arg(raw: str) -> str:
    mode = raw.strip().lower()
    return MODE_ALIAS.get(mode, mode)


def slugify(value: str) -> str:
    text = value.strip().lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = re.sub(r"-{2,}", "-", text).strip("-")
    return text[:64]


def load_requirements(path: Path) -> Dict[str, object]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return {
        "project_name": str(data.get("project_name", "New Project")).strip() or "New Project",
        "project_goal": str(data.get("project_goal", "待补充项目目标")).strip() or "待补充项目目标",
        "target_users": str(data.get("target_users", "待补充目标用户")).strip() or "待补充目标用户",
        "team_size": max(to_int(data.get("team_size"), 2), 1),
        "module_count": max(to_int(data.get("module_count"), 3), 1),
        "ui_priority": normalize_level(data.get("ui_priority"), "medium"),
        "backend_complexity": normalize_level(data.get("backend_complexity"), "medium"),
        "domain_complexity": normalize_level(data.get("domain_complexity"), "low"),
        "compliance_level": normalize_level(data.get("compliance_level"), "low"),
        "design_source": normalize_design(data.get("design_source"), "none"),
        "frontend_backend_separation": normalize_bool(data.get("frontend_backend_separation"), False),
        "need_fast_validation": normalize_bool(data.get("need_fast_validation"), True),
        "iteration_speed": normalize_speed(data.get("iteration_speed"), "normal"),
    }


def find_requirement_quality_issues(req: Dict[str, object]) -> List[str]:
    placeholder_hints = {
        "待补充",
        "todo",
        "tbd",
        "to be determined",
        "new project",
        "example",
        "示例",
        "unknown",
        "未定",
    }
    required_fields = {
        "project_name": "项目名称",
        "project_goal": "项目目标",
        "target_users": "目标用户",
    }

    issues: List[str] = []

    for key, label in required_fields.items():
        raw = str(req.get(key, "")).strip()
        lowered = raw.lower()

        if not raw:
            issues.append(f"{label} 为空")
            continue

        if "<" in raw or ">" in raw:
            issues.append(f"{label} 仍包含模板占位符")
            continue

        if any(token in lowered for token in placeholder_hints):
            issues.append(f"{label} 仍是占位/示例文本：{raw}")
            continue

        if key == "project_goal" and len(raw) < 8:
            issues.append("项目目标过短，建议写清业务结果与验收口径")

    return issues


def score_combos(req: Dict[str, object]) -> Dict[str, int]:
    team = int(req["team_size"])
    modules = int(req["module_count"])
    ui = LEVEL_MAP[str(req["ui_priority"])]
    backend = LEVEL_MAP[str(req["backend_complexity"])]
    domain = LEVEL_MAP[str(req["domain_complexity"])]
    compliance = LEVEL_MAP[str(req["compliance_level"])]
    design = str(req["design_source"])
    separation = bool(req["frontend_backend_separation"])
    fast = bool(req["need_fast_validation"])
    speed = SPEED_MAP[str(req["iteration_speed"])]

    score = {k: 2 for k in COMBO_VALUES}

    if team <= 2:
        score["c1"] += 2
    if modules <= 3:
        score["c1"] += 2
    if fast:
        score["c1"] += 2
    if design in {"none", "wireframe"}:
        score["c1"] += 1
    score["c1"] += max(0, 1 - domain)
    if compliance >= 1:
        score["c1"] -= 1

    if 2 <= team <= 5:
        score["c2"] += 2
    if 3 <= modules <= 8:
        score["c2"] += 2
    if speed >= 1:
        score["c2"] += 2
    if domain >= 1:
        score["c2"] += 1
    if fast:
        score["c2"] += 1

    if separation:
        score["c3"] += 3
    if backend >= 1:
        score["c3"] += 2
    if modules >= 4:
        score["c3"] += 2
    if compliance >= 1:
        score["c3"] += 1

    if design == "figma":
        score["c4"] += 4
    if ui == 2:
        score["c4"] += 3
    if fast:
        score["c4"] += 1
    if domain == 2:
        score["c4"] -= 1

    if fast:
        score["c5"] += 3
    if team <= 3:
        score["c5"] += 2
    if speed == 2:
        score["c5"] += 2
    if modules <= 5:
        score["c5"] += 1
    if domain == 2:
        score["c5"] -= 1

    if domain == 2:
        score["c6"] += 4
    if compliance >= 1:
        score["c6"] += 2
    if team >= 5:
        score["c6"] += 2
    if modules >= 6:
        score["c6"] += 2
    if fast:
        score["c6"] -= 1

    return score


def complexity_level(req: Dict[str, object]) -> str:
    team = int(req["team_size"])
    modules = int(req["module_count"])
    domain = LEVEL_MAP[str(req["domain_complexity"])]
    compliance = LEVEL_MAP[str(req["compliance_level"])]
    backend = LEVEL_MAP[str(req["backend_complexity"])]
    separation = 1 if bool(req["frontend_backend_separation"]) else 0

    score = 0
    if team <= 2:
        score += 0
    elif team <= 5:
        score += 1
    elif team <= 8:
        score += 2
    else:
        score += 3

    if modules <= 3:
        score += 0
    elif modules <= 6:
        score += 1
    elif modules <= 10:
        score += 2
    else:
        score += 3

    score += domain + compliance + backend + separation

    if score <= 4:
        return "S"
    if score <= 7:
        return "M"
    if score <= 10:
        return "L"
    return "XL"


def recommend_mode(req: Dict[str, object], complexity: str, forced_mode: str) -> str:
    if forced_mode in MODE_VALUES:
        return forced_mode
    compliance = LEVEL_MAP[str(req["compliance_level"])]
    if complexity == "S" and bool(req["need_fast_validation"]):
        return "minimal"
    if complexity == "XL" or compliance == 2:
        return "full"
    return "standard"


def select_combo(scores: Dict[str, int], forced_combo: str) -> Tuple[str, Optional[str]]:
    ordered = sorted(scores.items(), key=lambda item: (-item[1], item[0]))

    if forced_combo in COMBO_VALUES:
        secondary = ordered[0][0] if ordered and ordered[0][0] != forced_combo else (ordered[1][0] if len(ordered) > 1 else None)
        return forced_combo, secondary

    primary = ordered[0][0]
    secondary = None
    if len(ordered) > 1 and (ordered[0][1] - ordered[1][1]) <= 2:
        secondary = ordered[1][0]
    return primary, secondary


def combo_focus(primary: Combo) -> str:
    if primary.code == "c1":
        return "重点用需求画布和原型澄清需求，确保快速起步不跑偏。"
    if primary.code == "c2":
        return "重点按 Story 切片迭代，每轮都可交付可验证结果。"
    if primary.code == "c3":
        return "重点先定场景和接口契约，控制联调成本。"
    if primary.code == "c4":
        return "重点对齐设计稿与实现约束，避免只还原视觉。"
    if primary.code == "c5":
        return "重点做 MVP 假设与反馈闭环，快速验证价值。"
    if primary.code == "c6":
        return "重点先划分领域边界，确保后续可扩展与可治理。"
    return "重点围绕主组合推进。"


def build_reasons(req: Dict[str, object], combo_code: str) -> List[str]:
    reasons: List[str] = ["所有组合统一使用 Epic -> Feature/Story -> Core Spec 作为执行基座"]

    if combo_code == "c1":
        if int(req["team_size"]) <= 2:
            reasons.append("团队规模较小，先用需求画布和原型降低沟通成本")
        if int(req["module_count"]) <= 3:
            reasons.append("模块较少，适合快速出可运行版本")
    elif combo_code == "c2":
        reasons.append("项目需要持续迭代，Story 切片更容易稳定交付")
        if int(req["module_count"]) >= 3:
            reasons.append("中等模块规模适合按迭代分批推进")
    elif combo_code == "c3":
        reasons.append("前后端分离/接口协作需求明显，契约先行更稳")
        if str(req["backend_complexity"]) in {"medium", "high"}:
            reasons.append("后端复杂度偏高，先定 API 可降低联调成本")
    elif combo_code == "c4":
        reasons.append("项目强调视觉和交互，设计驱动路径更高效")
        reasons.append("可通过设计稿到 Prompt 映射避免只还原界面")
    elif combo_code == "c5":
        reasons.append("当前目标偏验证，MVP 路线可最低成本试错")
        reasons.append("反馈闭环可以快速驱动下一轮迭代")
    elif combo_code == "c6":
        reasons.append("领域复杂或合规要求较高，先做领域边界更安全")
        reasons.append("DDD 精简骨架能减少后续结构性返工")

    return reasons[:4]


def planned_docs(primary_combo: str, mode: str) -> List[Tuple[str, str]]:
    if mode == "single-file":
        return [SINGLE_FILE_DOC]

    docs = list(BASELINE_DOCS)
    docs.extend(BASE_DOCS)
    docs.extend(COMBO_MIN_DOCS[primary_combo])
    if mode in {"standard", "full"}:
        docs.extend(STANDARD_DOCS)
    if mode == "full":
        docs.extend(FULL_DOCS)
    return docs


def write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def ensure_writable_output_root(requested_root: Path) -> Path:
    fallback_root = Path("/tmp/umx-tools-v3/umx-doc-pack")
    candidates = [requested_root.expanduser(), fallback_root]

    for candidate in candidates:
        try:
            candidate.mkdir(parents=True, exist_ok=True)
            probe = candidate / ".umx-write-test"
            probe.write_text("ok", encoding="utf-8")
            probe.unlink(missing_ok=True)
            return candidate
        except OSError:
            continue

    raise SystemExit(
        "Unable to write output folder. Tried requested path and /tmp/umx-tools-v3/umx-doc-pack. "
        "Use --print-only and check filesystem permissions."
    )


def single_file_body(
    req: Dict[str, object],
    primary: Combo,
    secondary: Optional[Combo],
    mode: str,
    complexity: str,
) -> str:
    name = str(req["project_name"])
    goal = str(req["project_goal"])
    users = str(req["target_users"])
    today = datetime.now().strftime("%Y-%m-%d")
    reasons = build_reasons(req, primary.code)
    reason_lines = "\n".join(f"- {item}" for item in reasons)

    return f"""# UMX 单文件项目文档包

## 0. 基本信息

- 项目：{name}
- 日期：{today}
- 目标：{goal}
- 目标用户：{users}
- 主组合：{primary.code} {primary.name}
- 副组合：{secondary.code + ' ' + secondary.name if secondary else '无'}
- 文档模式：{mode}
- 复杂度：{complexity}
- 基座：Epic -> Feature/Story -> Core Spec

## 0.1 执行护栏（防幻觉 / 防上下文丢失 / 防 Bug 循环）

- 单一事实源：需求、范围、验收一律以本文件为准。
- 禁止新增：未写在 M0 范围内的需求不得实现。
- 小步提交：每次只改 1 个 Story，并回写变更原因。
- 先对齐再编码：代码实现前先核对 Epic/Story/Spec 是否一致。
- 失败先回文档：出现冲突或歧义时，先更新文档再继续实现。

## 1. 组合决策

### 选择理由

{reason_lines}

### 组合推进重点

- {combo_focus(primary)}

## 2. Epic Map

### 总 Epic

- 作为项目负责人，我希望在 M0 内实现“{goal}”，以便尽快验证业务价值。

### 子 Epic（M0）

1. 作为用户，我希望完成核心主流程，以便拿到可验证结果。
2. 作为系统，我希望具备最小错误处理能力，以便故障可定位。
3. 作为团队，我希望约束范围清晰，以便避免 M0 需求膨胀。

### 非目标

- 不引入 M1/M2 扩展能力。
- 不做与主流程无关的优化。

## 3. Feature Story Map

| Feature | 用户故事 | 验收标准 |
|---|---|---|
| F1 核心流程 | 作为用户，我希望完成一次主流程操作，以便拿到可用结果。 | 端到端一次通过 |
| F2 数据记录 | 作为系统，我希望记录关键状态与结果，以便可追踪。 | 查询可回放 |
| F3 错误处理 | 作为用户，我希望在失败时看到明确错误信息，以便知道如何处理。 | 错误码与提示一致 |

## 4. Core Spec

### 4.1 M0 范围

#### 做

- [ ] 核心主流程可跑通
- [ ] 最小数据模型落地
- [ ] 最小接口契约可联调

#### 不做

- [ ] M1/M2 扩展功能
- [ ] 非必要性能优化
- [ ] 高复杂运营能力

### 4.2 核心流程

1. 用户触发核心动作
2. 系统执行业务处理
3. 返回可验证结果
4. 失败时按统一错误格式返回

### 4.3 API 契约（最小）

| 接口 | 方法 | 输入 | 输出 | 错误码 |
|---|---|---|---|---|
| /api/v1/example | POST | 待补充 | 待补充 | E400/E500 |

### 4.4 数据模型（最小）

| 实体 | 关键字段 | 说明 |
|---|---|---|
| primary_entity | id/status/created_at | 待补充 |

### 4.5 异常与降级

- 参数校验失败：返回 E400
- 上游异常：返回 E502，并记录 trace_id
- 超时：返回 E504，并给出重试建议

### 4.6 验收清单

- [ ] 主流程端到端通过
- [ ] 错误场景可复现且可回归
- [ ] Epic/Story/Spec 一致

## 5. 里程碑计划

### M0

- 第 1 天：完成 Epic/Feature/Story 与 Core Spec 基座。
- 第 2-3 天：实现核心主链路。
- 第 4 天：异常处理 + 验收 + 文档回写。

### M1

- 拆分 API 与 DB 文档。
- 增加监控与回归脚本。

### M2

- 团队化协作文档。
- 版本治理与变更流程。

## 6. AI 执行 Prompt 包

### Prompt 0：执行前一致性闸门

```text
在开始编码前，请先输出以下检查结果：
1) 当前实现目标对应哪个 Epic 和 Story；
2) 该 Story 的验收标准；
3) 本次明确不做的内容（防范围膨胀）。
若无法明确，请先提问，不得直接编码。
```

### Prompt 1：实现 M0

```text
你是资深工程师。请严格按照本文件中的 Epic/Feature/Story/Core Spec 实现 M0，不得新增 M1/M2 内容。
要求：
1) 先输出实现计划；
2) 再分步实现；
3) 每步后给出自检结果；
4) 如遇冲突，以 Core Spec 为准并回写文档。
```

### Prompt 2：回归与验收

```text
请基于本文件执行回归检查。
输出：通过项、失败项、修复优先级。
禁止新增需求。
```

### Prompt 3：一致性审查

```text
请检查 Epic/Feature/Story/Core Spec/接口/数据结构是否一致。
输出不一致项及修复建议，按高/中/低优先级排序。
```

## 7. 组合专属补充（{primary.code}）

- 组合流程：{primary.pipeline}
- 适用场景：{primary.fit}
- 当前建议：{combo_focus(primary)}

## 8. 下一步执行

1. 先补完 API 与数据模型中的待补充项。
2. 用 Prompt 1 驱动 AI 完成 M0 实现。
3. 回归后按需要升级为 standard/full 多文件模式。
"""


def doc_body(
    filename: str,
    title: str,
    req: Dict[str, object],
    primary: Combo,
    secondary: Optional[Combo],
    mode: str,
    complexity: str,
) -> str:
    name = str(req["project_name"])
    goal = str(req["project_goal"])
    users = str(req["target_users"])
    secondary_text = f"（副组合：{secondary.code} {secondary.name}）" if secondary else ""
    today = datetime.now().strftime("%Y-%m-%d")

    if filename == "00-epic-map.md":
        return f"""# Epic Map

- 项目名称：{name}
- 日期：{today}
- 主组合：{primary.code} {primary.name} {secondary_text}

## 总 Epic

- 作为项目负责人，我希望在 M0 内实现“{goal}”，以便尽快验证业务价值。

## 子 Epic（M0）

1. 作为用户，我希望完成核心主流程，以便拿到可验证结果。
2. 作为系统，我希望具备最小错误处理能力，以便故障可定位。
3. 作为团队，我希望约束范围清晰，以便避免 M0 需求膨胀。

## 非目标

- 不引入 M1/M2 扩展能力。
- 不做与主流程无关的优化。
"""

    if filename == "01-feature-story-map.md":
        return f"""# Feature Story Map

## 对齐信息

- 目标用户：{users}
- 目标：{goal}

## Feature 列表（M0）

| Feature | 用户故事 | 验收标准 |
|---|---|---|
| F1 核心流程 | 作为用户，我希望完成一次主流程操作，以便拿到可用结果。 | 端到端一次通过 |
| F2 数据记录 | 作为系统，我希望记录关键状态与结果，以便可追踪。 | 查询可回放 |
| F3 错误处理 | 作为用户，我希望在失败时看到明确错误信息，以便知道如何处理。 | 错误码与提示一致 |

## 执行规则

- Story 只能实现 M0 范围。
- 每条 Story 必须映射到 `02-core-spec.md`。
"""

    if filename == "02-core-spec.md":
        return f"""# Core Spec

## 1. 一句话定义

{name}：{goal}

## 2. M0 范围

### 做

- [ ] 核心主流程可跑通
- [ ] 最小数据模型落地
- [ ] 最小接口契约可联调

### 不做

- [ ] M1/M2 扩展功能
- [ ] 非必要性能优化
- [ ] 高复杂运营能力

## 3. 核心流程

1. 用户触发核心动作
2. 系统执行业务处理
3. 返回可验证结果
4. 失败时按统一错误格式返回

## 4. API 契约（最小）

| 接口 | 方法 | 输入 | 输出 | 错误码 |
|---|---|---|---|---|
| /api/v1/example | POST | 待补充 | 待补充 | E400/E500 |

## 5. 数据模型（最小）

| 实体 | 关键字段 | 说明 |
|---|---|---|
| primary_entity | id/status/created_at | 待补充 |

## 6. 异常与降级

- 参数校验失败：返回 E400
- 上游异常：返回 E502，并记录 trace_id
- 超时：返回 E504，并给出重试建议

## 7. 执行护栏

- 单一事实源：本文件 + `00-epic-map.md` + `01-feature-story-map.md`
- 禁止新增：未进入 M0 的需求不得进入代码实现
- 变更先回写：接口/数据结构变更必须先改文档再改代码
- 回归门禁：每次改动都要覆盖至少 1 条失败场景

## 8. 验收清单

- [ ] 主流程端到端通过
- [ ] 错误场景可复现且可回归
- [ ] 与 `00-epic-map.md` 和 `01-feature-story-map.md` 一致
"""

    if filename == "03-combo-decision.md":
        reasons = build_reasons(req, primary.code)
        reason_lines = "\n".join(f"- {item}" for item in reasons)
        return f"""# 组合决策记录

## 结果

- 主组合：{primary.code} {primary.name}
- 副组合：{secondary.code + ' ' + secondary.name if secondary else '无'}
- 文档模式：{mode}
- 复杂度：{complexity}
- 基座：Epic -> Feature/Story -> Core Spec（固定）

## 选择理由

{reason_lines}

## 复盘时机

- M0 结束后评估是否切换/叠加组合。
"""

    if filename == "04-milestone-plan.md":
        return """# 里程碑计划

## M0（当前阶段）

- 第 1 天：完成 Epic/Feature/Story 与 Core Spec 基座。
- 第 2-3 天：实现核心主链路。
- 第 4 天：异常处理 + 验收 + 文档回写。

## M1（预留）

- 拆分 API 与 DB 文档。
- 增加监控与回归脚本。

## M2（预留）

- 团队化协作文档。
- 版本治理与变更流程。
"""

    if filename == "05-ai-prompt-pack.md":
        return """# AI 执行 Prompt 包

## Prompt 0：执行前一致性闸门

```text
在开始编码前，请先输出以下检查结果：
1) 本次实现对应的 Epic 与 Story 编号；
2) 对应验收标准；
3) 本次不做内容（明确范围边界）。
若无法明确，请先提问，不得直接编码。
```

## Prompt 1：实现 M0 主流程

```text
你是资深工程师。请严格按照 `00-epic-map.md`、`01-feature-story-map.md`、`02-core-spec.md` 实现 M0，不得新增 M1/M2 内容。
要求：
1) 先输出实现计划；
2) 再分步实现；
3) 每步后给出自检结果；
4) 如遇冲突，以 `02-core-spec.md` 为准并回写文档。
```

## Prompt 2：回归与验收

```text
请基于 `00-epic-map.md`、`01-feature-story-map.md`、`02-core-spec.md`、`04-milestone-plan.md` 执行回归检查。
输出：
- 通过项
- 失败项
- 修复优先级
- 不允许新增需求
```

## Prompt 3：文档一致性审查

```text
请检查 Epic/Feature/Story/Core Spec/接口/数据结构是否一致。
输出不一致项及修复建议，按高/中/低优先级排序。
```
"""

    if filename == "10-prd-lite.md":
        return f"""# PRD Lite

## 背景与目标

- 背景：{goal}
- 目标用户：{users}

## 范围

### 做

- 待补充

### 不做

- 待补充

## 指标

- 待补充（如转化率、完成率、时延）

## 与基座映射

- 需求 -> `00-epic-map.md`
- Story -> `01-feature-story-map.md`
- 约束 -> `02-core-spec.md`
"""

    if filename == "11-architecture-lite.md":
        return """# Architecture Lite

## 分层结构

- 展示层
- 应用层
- 领域层
- 基础设施层

## 模块边界

- 待补充模块及依赖关系

## 数据流

1. 请求进入
2. 业务处理
3. 数据持久化
4. 响应返回

## 与基座映射

- `02-core-spec.md` 为唯一实现约束。
"""

    if filename == "12-api-spec.md":
        return """# API Spec

## 接口列表

| 路径 | 方法 | 描述 | 权限 |
|---|---|---|---|
| /api/v1/example | POST | 待补充 | user |

## 请求与响应示例

```json
{
  "todo": "补充请求响应示例"
}
```

## 错误码

| code | message | 说明 |
|---|---|---|
| E400 | Bad Request | 参数错误 |
| E500 | Internal Error | 服务异常 |

## 对齐规则

- 与 `02-core-spec.md` 保持一致。
"""

    if filename == "13-database-design.md":
        return """# Database Design

## 表结构

| 表名 | 字段 | 类型 | 约束 | 说明 |
|---|---|---|---|---|
| example_table | id | bigint | pk | 主键 |

## 索引策略

- 待补充

## 迁移策略

- 正向迁移
- 回滚策略

## 对齐规则

- 与 `02-core-spec.md` 和 `12-api-spec.md` 字段一致。
"""

    if filename == "14-risk-checklist.md":
        return """# 风险与回归清单

## 主要风险

- 需求漂移
- 接口不一致
- 数据结构变更风险

## 回归项

- [ ] Epic/Story/Spec 一致
- [ ] 主流程可用
- [ ] 异常场景覆盖
- [ ] 文档与代码一致
"""

    if filename == "20-module-spec-index.md":
        return """# 模块 Spec 索引

- module-a-spec.md
- module-b-spec.md
- module-c-spec.md

> 每个模块 Spec 必须包含：边界、输入输出、状态、错误、验收。
"""

    if filename == "21-test-regression-plan.md":
        return """# 测试与回归计划

## 回归层级

1. 单元测试
2. 接口测试
3. 端到端测试

## 回归节奏

- 每次合并前执行最小回归
- 每次里程碑结束执行全量回归
"""

    if filename == "22-ops-runbook.md":
        return """# 运维 Runbook

## 部署步骤

1. 构建
2. 发布
3. 健康检查

## 监控指标

- 错误率
- 时延
- 资源占用

## 故障处理

- 回滚条件
- 告警升级路径
"""

    if filename == "23-change-log-governance.md":
        return """# 变更治理

## 变更分类

- 功能变更
- 契约变更
- 数据变更

## 评审机制

- 变更前评审
- 变更后回归
- 文档同步更新
"""

    return f"""# {title}

> 项目：{name}

## 目标

- 待补充：该文档在当前组合中的作用

## 内容

- 待补充：关键约束、流程、数据、验收

## 与基座关联

- 对应 `00-epic-map.md` / `01-feature-story-map.md` / `02-core-spec.md` 章节：待补充
"""


def report_markdown(
    req: Dict[str, object],
    scores: Dict[str, int],
    primary: Combo,
    secondary: Optional[Combo],
    mode: str,
    complexity: str,
    docs: List[Tuple[str, str]],
) -> str:
    lines = [
        "# 选型与文档包报告",
        "",
        "## 1. 输入摘要",
        "",
        f"- 项目：{req['project_name']}",
        f"- 目标：{req['project_goal']}",
        f"- 团队规模：{req['team_size']}",
        f"- 模块数：{req['module_count']}",
        f"- UI 优先级：{req['ui_priority']}",
        f"- 后端复杂度：{req['backend_complexity']}",
        f"- 领域复杂度：{req['domain_complexity']}",
        f"- 合规等级：{req['compliance_level']}",
        "",
        "## 2. 组合评分",
        "",
        "| 组合 | 流程 | 分数 |",
        "|---|---|---|",
    ]
    for code, score in sorted(scores.items(), key=lambda item: (-item[1], item[0])):
        combo = COMBOS[code]
        lines.append(f"| {code} | {combo.pipeline} | {score} |")

    lines.extend(
        [
            "",
            "## 3. 推荐结果",
            "",
            f"- 主组合：{primary.code} {primary.name}",
            f"- 副组合：{secondary.code + ' ' + secondary.name if secondary else '无'}",
            f"- 复杂度：{complexity}",
            f"- 文档模式：{mode}",
            "- 固定基座：Epic -> Feature/Story -> Core Spec",
            "",
            "### 主组合理由",
            "",
        ]
    )

    for reason in build_reasons(req, primary.code):
        lines.append(f"- {reason}")

    lines.extend(["", "## 4. 文档清单", ""])
    for filename, title in docs:
        lines.append(f"- `{filename}`: {title}")

    lines.extend(
        [
            "",
            "## 5. 下一步执行",
            "",
            "1. 先补全 Epic/Feature/Story/Core Spec 基座。",
            "2. 再执行组合层文档和 M0 实现。",
            "3. 每次变更后同步更新组合决策与里程碑。",
        ]
    )
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a project document pack from requirements JSON")
    parser.add_argument("--input", required=True, help="Path to requirements JSON file")
    parser.add_argument("--output", default="./umx-doc-pack", help="Output directory root")
    parser.add_argument("--combo", default="auto", help="auto or one of c1..c6")
    parser.add_argument("--mode", default="auto", help="auto/minimal/standard/full/single-file")
    parser.add_argument("--project-slug", default="", help="Optional output folder slug")
    parser.add_argument("--print-only", action="store_true", help="Only print plan without writing files")
    parser.add_argument("--flat", action="store_true", help="Write files directly into output root without an extra slug folder")
    parser.add_argument("--allow-placeholder", action="store_true", help="Allow placeholder values in key requirement fields")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    combo_arg = args.combo.strip().lower()
    mode_arg = normalize_mode_arg(args.mode)

    if combo_arg != "auto" and combo_arg not in COMBO_VALUES:
        raise SystemExit(f"Invalid --combo: {combo_arg}")
    if mode_arg != "auto" and mode_arg not in MODE_VALUES:
        raise SystemExit(f"Invalid --mode: {mode_arg}")

    req = load_requirements(Path(args.input))

    if not args.allow_placeholder:
        quality_issues = find_requirement_quality_issues(req)
        if quality_issues:
            details = "\n".join(f"- {item}" for item in quality_issues)
            raise SystemExit(
                "Input quality check failed. Please complete concrete requirements before generating docs:\n"
                f"{details}\n"
                "Tip: this guardrail helps reduce hallucination/context-loss/bug-loop in follow-up AI coding. "
                "Use --allow-placeholder only for temporary drafts."
            )

    scores = score_combos(req)
    primary_code, secondary_code = select_combo(scores, combo_arg)
    complexity = complexity_level(req)
    mode = recommend_mode(req, complexity, mode_arg)

    primary = COMBOS[primary_code]
    secondary = COMBOS[secondary_code] if secondary_code else None

    docs = planned_docs(primary_code, mode)
    report = report_markdown(req, scores, primary, secondary, mode, complexity, docs)

    if args.print_only:
        print(report)
        return

    requested_output = Path(args.output)
    writable_output = ensure_writable_output_root(requested_output)
    try:
        requested_resolved = requested_output.expanduser().resolve()
        writable_resolved = writable_output.resolve()
        if writable_resolved != requested_resolved:
            print(f"Warning: output path not writable, fallback to {writable_output}")
    except OSError:
        pass

    if args.flat:
        out_root = writable_output
    else:
        base_slug = args.project_slug.strip() or slugify(str(req["project_name"]))
        if not base_slug:
            base_slug = f"project-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        out_root = writable_output / base_slug

    out_root.mkdir(parents=True, exist_ok=True)

    generated_files = 0

    if mode == "single-file":
        single_name, _ = SINGLE_FILE_DOC
        write_file(out_root / single_name, single_file_body(req, primary, secondary, mode, complexity))
        generated_files = 1
    else:
        write_file(out_root / "selection-report.md", report)
        generated_files = 1
        for filename, title in docs:
            write_file(out_root / filename, doc_body(filename, title, req, primary, secondary, mode, complexity))
            generated_files += 1

    print(f"Generated: {out_root}")
    print(f"Primary combo: {primary.code} {primary.name}")
    print(f"Secondary combo: {secondary.code + ' ' + secondary.name if secondary else 'none'}")
    print(f"Complexity: {complexity}")
    print(f"Doc mode: {mode}")
    print("Baseline: 00-epic-map.md -> 01-feature-story-map.md -> 02-core-spec.md")
    print(f"Files: {generated_files}")


if __name__ == "__main__":
    main()
