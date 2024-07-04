from __future__ import annotations

from typing import Any, Callable


class Input:
    def __init__(self, node: Node) -> None:
        self.node = node
        self.buffer = None


class Output:
    def __init__(self, node: Node) -> None:
        self.node = node
        self.buffer = None


class Node:
    def __init__(self) -> None:
        self.inputs: dict[str, Input] = {}
        self.outputs: dict[str, Output] = {}
