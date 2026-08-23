"""Command-line interface for skill-video-script."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Sequence, TextIO

from .errors import InputError, VideoScriptError
from .generator import generate
from .io_util import load_brief_from_path, write_output
from .llm import LLMClient, make_enhancer
from .render import render_json, render_markdown
from .validate import parse_brief


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="video-script",
        description="Generate 3-style short-video scripts for Douyin, WeChat Channels, and Bilibili.",
    )
    parser.add_argument(
        "input",
        nargs="?",
        help="JSON file with the product brief, or '-' to read stdin",
    )
    parser.add_argument("--name", help="Product name")
    parser.add_argument("--platform", help="douyin | wechat | bilibili (or 抖音/视频号/B站)")
    parser.add_argument("--points", help="Selling points, comma-separated")
    parser.add_argument("--audience", default=None)
    parser.add_argument("--category", default=None)
    parser.add_argument("--price", default=None)
    parser.add_argument("--brand", default=None)
    parser.add_argument("--description", default=None)
    parser.add_argument("--duration", type=int, default=None, help="Target duration in seconds")
    parser.add_argument("--language", default=None, help="zh or en (copy is Chinese for CN platforms)")
    parser.add_argument(
        "--backend",
        choices=("template", "llm"),
        default="template",
        help="template (default, offline) or llm (requires VIDEO_SCRIPT_API_KEY)",
    )
    parser.add_argument(
        "--format",
        choices=("md", "json", "both"),
        default="md",
        dest="fmt",
    )
    parser.add_argument("-o", "--output", help="Output file path (directories are created)")
    parser.add_argument("--stdout", action="store_true", help="Force printing to stdout even if --output is set")
    return parser


def _brief_from_args(args: argparse.Namespace, stdin: TextIO) -> Any:
    payload: dict[str, Any] = {}
    if args.input:
        if args.input == "-":
            text = stdin.read()
            if not text.strip():
                raise InputError("stdin is empty")
            try:
                payload = json.loads(text)
            except json.JSONDecodeError as exc:
                raise InputError(f"stdin is not valid JSON: {exc.msg}") from exc
            if not isinstance(payload, dict):
                raise InputError("stdin JSON must be an object")
        else:
            return load_brief_from_path(Path(args.input))
    cli_fields = {
        "name": args.name,
        "platform": args.platform,
        "selling_points": args.points,
        "audience": args.audience,
        "category": args.category,
        "price": args.price,
        "brand": args.brand,
        "description": args.description,
        "duration_sec": args.duration,
        "language": args.language,
    }
    for key, value in cli_fields.items():
        if value is not None:
            payload[key] = value
    if not payload:
        raise InputError("provide a JSON file or --name/--platform/--points")
    return parse_brief(payload)


def main(argv: Sequence[str] | None = None, *, stdin: TextIO | None = None, stdout: TextIO | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)
    in_stream = stdin if stdin is not None else sys.stdin
    out_stream = stdout if stdout is not None else sys.stdout
    try:
        brief = _brief_from_args(args, in_stream)
        enhancer = None
        if args.backend == "llm":
            client = LLMClient()
            client.require_ready()
            enhancer = make_enhancer(client)
        result = generate(brief, backend=args.backend, enhancer=enhancer)
        rendered: dict[str, str] = {}
        if args.fmt in {"md", "both"}:
            rendered["md"] = render_markdown(result)
        if args.fmt in {"json", "both"}:
            rendered["json"] = render_json(result)
        if args.output:
            base = Path(args.output)
            if args.fmt == "both":
                write_output(base.with_suffix(".md"), rendered["md"])
                write_output(base.with_suffix(".json"), rendered["json"])
            else:
                write_output(base, next(iter(rendered.values())))
        if args.stdout or not args.output:
            for content in rendered.values():
                out_stream.write(content)
                if not content.endswith("\n"):
                    out_stream.write("\n")
        return 0
    except VideoScriptError as exc:
        sys.stderr.write(f"error: {exc}\n")
        return int(getattr(exc, "exit_code", 1) or 1)
    except BrokenPipeError:
        return 0
