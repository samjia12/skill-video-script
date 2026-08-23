"""Filesystem helpers with explicit permission errors."""

from __future__ import annotations

import json
import os
from pathlib import Path

from .errors import AccessDeniedError, EmptyInputError, InputError
from .validate import parse_brief


def read_text(path: Path, *, encoding: str = "utf-8") -> str:
    try:
        return Path(path).read_text(encoding=encoding)
    except FileNotFoundError as exc:
        raise InputError(f"input file not found: {path}") from exc
    except PermissionError as exc:
        raise AccessDeniedError(f"cannot read {path}: permission denied") from exc
    except OSError as exc:
        raise AccessDeniedError(f"cannot read {path}: {exc}") from exc


def load_brief_from_path(path: Path):
    text = read_text(path)
    if not text.strip():
        raise EmptyInputError("input file is empty")
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        raise InputError(f"{path} is not valid JSON: {exc.msg}") from exc
    return parse_brief(payload)


def write_output(path: Path, content: str, *, encoding: str = "utf-8") -> Path:
    """Atomically write text. Directories are created when missing."""
    path = Path(path)
    try:
        exists = path.exists()
        is_dir = path.is_dir() if exists else False
    except PermissionError as exc:
        raise AccessDeniedError(f"cannot access {path}: permission denied") from exc
    except OSError as exc:
        raise AccessDeniedError(f"cannot access {path}: {exc}") from exc
    if exists and is_dir:
        raise InputError(f"output path is a directory: {path}")
    if exists and not os.access(path, os.W_OK):
        raise AccessDeniedError(f"cannot write {path}: permission denied")
    parent = path.parent if str(path.parent) else Path(".")
    try:
        parent.mkdir(parents=True, exist_ok=True)
    except PermissionError as exc:
        raise AccessDeniedError(f"cannot create directory {parent}: permission denied") from exc
    except OSError as exc:
        raise AccessDeniedError(f"cannot create directory {parent}: {exc}") from exc

    tmp = path.with_name(path.name + ".tmp")
    try:
        fd = os.open(str(tmp), os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o644)
    except PermissionError as exc:
        raise AccessDeniedError(f"cannot write {path}: permission denied") from exc
    except OSError as exc:
        raise AccessDeniedError(f"cannot write {path}: {exc}") from exc
    try:
        with os.fdopen(fd, "w", encoding=encoding) as handle:
            handle.write(content)
        os.replace(str(tmp), str(path))
    except PermissionError as exc:
        raise AccessDeniedError(f"cannot write {path}: permission denied") from exc
    except OSError as exc:
        raise AccessDeniedError(f"cannot write {path}: {exc}") from exc
    finally:
        if tmp.exists():
            try:
                tmp.unlink()
            except OSError:
                pass
    return path
