from __future__ import annotations

from typing import Any, Callable


class Input:
    def __init__(self, node: Node) -> None:
        self.node = node
        self.source = None

    def link(self, source: Output) -> None:
        self.source = source

    def read(self, offset: int, duration: int) -> Any:
        if self.source is None:
            raise RuntimeError('input cannot be read from as it has no source')

        return self.source.render(offset, duration)


class Output:
    def __init__(self, node: Node, func: Callable[[int, int], Any]) -> None:
        self.node = node
        self._render_func = func
        self.render_cache: tuple[tuple[int, int], Any] = (0, 0), None

    def render(self, offset: int, duration: int) -> Any:
        if self.render_cache[0] != (offset, duration) or self.render_cache[1] is None:
            self.render_cache = (offset, duration), self._render_func(offset, duration)

        return self.render_cache[1]


class Node:
    def __init__(self) -> None:
        self.inputs: dict[str, Input] = {}
        self.outputs: dict[str, Output] = {}
