#!/usr/bin/env python3
"""UMX V3 flow runner.

Routes:
- ask
- traditional-first
- direct

Supports command mode:
- /umx start
- /umx traditional --docs ... --combo ... --mode ...
- /umx direct --combo ... --mode ...
- /umx recommend --mode ...
"""

from __future__ import annotations

import argparse
import json
import shlex
import subprocess
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

VALID_PATHS = {"ask", "traditional-first", "direct"}
VALID_DOCS = ["prd", "architecture", "api", "database"]
DOC_ALIAS = {
    "prd": "prd",
    "product": "prd",
    "architecture": "architecture",
    "arch": "architecture",
    "api": "api",
    "database": "database",
    "db": "database",
}


@dataclass
class FlowConfig:
    input_path: Path
    output_root: Path
    path_choice: str
    combo: str
    mode: str
    traditional_docs: List[str]
    print_only: bool


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run UMX V3 flow")
    parser.add_argument("--input", required=True, help="Path to requirements JSON")
    parser.add_argument("--output", default="./umx-output", help="Root output directory")
    parser.add_argument("--path", default="ask", choices=sorted(VALID_PATHS), help="ask|traditional-first|direct")
    parser.add_argument("--traditional-docs", default="prd,architecture,api,database", help="Comma list")
    parser.add_argument("--combo", default="auto", help="auto or c1..c6")
    parser.add_argument("--mode", default="single-file", help="single-file|minimal|standard|full")
    parser.add_argument("--command", default="", help="Command mode input")
    parser.add_argument("--print-only", action="store_true", help="Plan only")
    return parser.parse_args()


def normalize_docs(raw: str) -> List[str]:
    items = [x.strip().lower() for x in raw.split(",") if x.strip()]
    if not items:
        items = list(VALID_DOCS)

    picked: List[str] = []
    for item in items:
        key = DOC_ALIAS.get(item)
        if key and key not in picked:
            picked.append(key)

    if not picked:
        picked = list(VALID_DOCS)

    return [d for d in VALID_DOCS if d in picked]


def parse_command(raw: str) -> Dict[str, str]:
    cleaned = raw.strip()
    if not cleaned:
        return {}

    # Natural-language acceptance shortcuts often used in Claude Code CLI.
    if cleaned in {"接受推荐", "确认", "确认推荐", "确认方案", "开始生成", "开始生成文档", "接受"}:
        return {
            "path": "direct",
            "combo": "auto",
            "mode": "single-file",
        }

    tokens = shlex.split(cleaned)
    if not tokens:
        return {}

    if tokens[0] in {"/umx", "umx"}:
        tokens = tokens[1:]
    if not tokens:
        return {}

    action = tokens[0].lower()
    result: Dict[str, str] = {}

    if action == "start":
        result["path"] = "ask"
        return result
    if action == "traditional":
        result["path"] = "traditional-first"
    elif action == "direct":
        result["path"] = "direct"
    elif action == "recommend":
        result["recommend"] = "1"
    elif action in {"accept", "accepted", "accept-recommend"}:
        result["path"] = "direct"
        result["combo"] = "auto"
        result["mode"] = "single-file"
    else:
        return {}

    i = 1
    while i < len(tokens):
        key = tokens[i]
        if key.startswith("--") and i + 1 < len(tokens):
            val = tokens[i + 1]
            if key == "--docs":
                result["traditional_docs"] = val
            elif key == "--combo":
                result["combo"] = val
            elif key == "--mode":
                result["mode"] = val
            elif key == "--output":
                result["output"] = val
            elif key == "--path":
                result["path"] = val
            i += 2
            continue
        i += 1

    return result


def load_requirements(input_path: Path) -> Dict[str, str]:
    data = json.loads(input_path.read_text(encoding="utf-8"))
    return {
        "project_name": str(data.get("project_name", "New Project")).strip() or "New Project",
        "project_goal": str(data.get("project_goal", "待补充项目目标")).strip() or "待补充项目目标",
        "target_users": str(data.get("target_users", "待补充目标用户")).strip() or "待补充目标用户",
    }


def ensure_writable_root(requested: Path) -> Path:
    fallback = Path("/tmp/umx-tools-v3/umx-output")
    for root in [requested.expanduser(), fallback]:
        try:
            root.mkdir(parents=True, exist_ok=True)
            probe = root / ".umx-v3-write-test"
            probe.write_text("ok", encoding="utf-8")
            probe.unlink(missing_ok=True)
            return root
        except OSError:
            continue

    raise SystemExit("Unable to write output folder.")


def ask_text() -> str:
    return """# UMX V3 交互入口

请先确认：

1) 是否先生成传统文档？(yes/no)
2) 若 yes，需要哪些文档？(prd,architecture,api,database)
3) 若 no，是否直接进入组合选型？
4) 是否接受自动推荐组合？
5) 是否先用 single-file 启动？

命令示例：
- /umx traditional --docs prd,architecture,api,database --combo auto --mode minimal
- /umx direct --combo auto --mode single-file
"""


def write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def write_traditional_docs(output_dir: Path, req: Dict[str, str], docs: List[str]) -> List[str]:
    written: List[str] = []

    write_file(
        output_dir / "00-traditional-index.md",
        f"""# Traditional Docs Index

- 项目：{req['project_name']}
- 目标：{req['project_goal']}
- 路线：traditional-first
- 日期：{datetime.now().strftime('%Y-%m-%d')}
""",
    )
    written.append("00-traditional-index.md")

    templates: Dict[str, Tuple[str, str]] = {
        "prd": (
            "01-prd-lite.md",
            f"""# PRD Lite

## 背景与目标

- 项目：{req['project_name']}
- 目标：{req['project_goal']}
- 用户：{req['target_users']}

## 范围

- 做：统一注册登录、SSO 接入
- 不做：过度复杂权限体系
""",
        ),
        "architecture": (
            "02-architecture-lite.md",
            """# Architecture Lite

## 分层

- 前端层
- 服务层
- 数据层

## 核心模块

- 认证中心
- 授权中心
- 用户中心
- 接入管理
""",
        ),
        "api": (
            "03-api-spec.md",
            """# API Spec

| 路径 | 方法 | 说明 |
|---|---|---|
| /auth/register | POST | 注册 |
| /auth/login | POST | 登录 |
| /sso/authorize | GET | 授权 |
| /sso/token | POST | 换 token |
""",
        ),
        "database": (
            "04-database-design.md",
            """# Database Design

## 核心表

- users
- clients
- app_user_bindings
- access_tokens
- refresh_tokens
""",
        ),
    }

    for doc in docs:
        filename, body = templates[doc]
        write_file(output_dir / filename, body)
        written.append(filename)

    return written


def run_vibe_generator(config: FlowConfig) -> subprocess.CompletedProcess[str]:
    script = Path(__file__).resolve().parent / "generate_doc_pack.py"
    cmd = [
        "python3",
        str(script),
        "--input",
        str(config.input_path),
        "--output",
        str(config.output_root / "vibe-docs"),
        "--combo",
        config.combo,
        "--mode",
        config.mode,
        "--flat",
    ]
    if config.print_only:
        cmd.append("--print-only")

    return subprocess.run(cmd, check=True, text=True, capture_output=True)


def write_route_summary(root: Path, config: FlowConfig, req: Dict[str, str]) -> None:
    write_file(
        root / "route-summary.md",
        f"""# Route Summary

- 项目：{req['project_name']}
- 路线：{config.path_choice}
- 组合：{config.combo}
- 模式：{config.mode}
- 传统文档：{','.join(config.traditional_docs) if config.path_choice == 'traditional-first' else '无'}
""",
    )


def main() -> None:
    args = parse_args()

    overrides = parse_command(args.command)
    path_choice = overrides.get("path", args.path)
    combo = overrides.get("combo", args.combo)
    mode = overrides.get("mode", args.mode)
    output_arg = overrides.get("output", args.output)
    docs_arg = overrides.get("traditional_docs", args.traditional_docs)

    if path_choice not in VALID_PATHS:
        raise SystemExit(f"Invalid path: {path_choice}")

    input_path = Path(args.input)
    if not input_path.exists():
        raise SystemExit(f"Input JSON not found: {input_path}")

    req = load_requirements(input_path)

    if path_choice == "ask":
        print(ask_text())
        return

    if overrides.get("recommend") == "1":
        proc = subprocess.run(
            [
                "python3",
                str(Path(__file__).resolve().parent / "generate_doc_pack.py"),
                "--input",
                str(input_path),
                "--combo",
                "auto",
                "--mode",
                mode,
                "--print-only",
            ],
            check=True,
            text=True,
            capture_output=True,
        )
        print(proc.stdout)
        return

    docs = normalize_docs(docs_arg)

    requested_root = Path(output_arg)
    writable_root = ensure_writable_root(requested_root)
    if writable_root.resolve() != requested_root.expanduser().resolve():
        print(f"Warning: output path not writable, fallback to {writable_root}")

    # Keep output structure shallow by default:
    # <output>/traditional-docs and <output>/vibe-docs
    root = writable_root
    root.mkdir(parents=True, exist_ok=True)

    config = FlowConfig(
        input_path=input_path,
        output_root=root,
        path_choice=path_choice,
        combo=combo,
        mode=mode,
        traditional_docs=docs,
        print_only=args.print_only,
    )

    if args.print_only:
        print(f"Route: {config.path_choice}")
        print(f"Output root: {root}")
        if config.path_choice == "traditional-first":
            print(f"Traditional docs: {','.join(config.traditional_docs)}")
            print("Traditional dir: traditional-docs/")
        print("Vibe dir: vibe-docs/")
        vibe = run_vibe_generator(config)
        print(vibe.stdout)
        return

    write_route_summary(root, config, req)

    traditional_files: List[str] = []
    if config.path_choice == "traditional-first":
        traditional_files = write_traditional_docs(root / "traditional-docs", req, config.traditional_docs)

    vibe = run_vibe_generator(config)

    print(f"Generated root: {root}")
    print(f"Route: {config.path_choice}")
    if traditional_files:
        print(f"Traditional files: {len(traditional_files)}")
        print("Traditional dir: traditional-docs/")
    print("Vibe dir: vibe-docs/")
    print(vibe.stdout.strip())


if __name__ == "__main__":
    main()
