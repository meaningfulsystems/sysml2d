"""Minimal SysML textual reference index for v0.1 examples."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path


_DECL_RE = re.compile(
    r"\b(?P<kind>"
    r"package|part\s+def|port\s+def|state\s+def|constraint\s+def|interface\s+def|item\s+def|"
    r"use\s+case|analysis\s+case|verification\s+case|"
    r"part|port|state|connection|transition|requirement|action|interaction|"
    r"constraint|interface|item|flow|allocation|attribute"
    r")\s+(?P<name>[A-Za-z_][A-Za-z0-9_]*)"
)


@dataclass
class ModelIndex:
    names: set[str] = field(default_factory=set)

    def has(self, name: str) -> bool:
        return name in self.names


def build_model_index(paths: list[Path]) -> ModelIndex:
    index = ModelIndex()
    for path in paths:
        text = path.read_text(encoding="utf-8")
        package_stack: list[str] = []
        def_stack: list[str] = []
        for raw_line in text.splitlines():
            line = raw_line.strip()
            if not line or line.startswith("//"):
                continue
            if line.startswith("}"):
                if def_stack:
                    def_stack.pop()
                elif package_stack:
                    package_stack.pop()
                continue
            match = _DECL_RE.search(line)
            if not match:
                continue
            kind = match.group("kind")
            name = match.group("name")
            index.names.add(name)
            if line.startswith("package "):
                package_stack.append(name)
                index.names.add("::".join(package_stack))
                continue
            if kind in {"part def", "state def", "constraint def", "interface def", "item def"}:
                qualified = "::".join(package_stack + [name])
                index.names.add(qualified)
                if line.endswith("{"):
                    def_stack.append(name)
                continue
            owner = package_stack + def_stack
            if owner:
                index.names.add("::".join(owner + [name]))
            index.names.add("::".join(package_stack + [name]))
            if kind in {"state", "action", "interaction"} and line.endswith("{"):
                def_stack.append(name)
    return index
