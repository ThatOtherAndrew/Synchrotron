from __future__ import annotations

from typing import TYPE_CHECKING, Any

import numpy as np

if TYPE_CHECKING:
    from collections.abc import Callable


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


class ConstantNode(Node):
    def __init__(self, value: Any) -> None:
        super().__init__()
        self.outputs['value'] = Output(self, self.value)

        self.value = value

    def value(self, _: int, __: int) -> Any:
        return self.value


class SineNode(Node):
    def __init__(self) -> None:
        super().__init__()
        self.inputs['frequency'] = Input(self)
        self.outputs['sine'] = Output(self, self.sine)

    def sine(self, offset: int, duration: int):
        frequency = self.inputs['frequency'].read(offset, duration)
        sine_window = np.linspace(
            0,
            2 * np.pi * frequency * 44100 / duration,
            num=duration,
            endpoint=False,
            dtype=np.float32
        )
        return np.sin(sine_window)


class DebugNode(Node):
    def __init__(self) -> None:
        super().__init__()
        self.inputs['in'] = Input(self)
        self.outputs['out'] = Output(self, self.out)

    def out(self, offset: int, duration: int) -> Any:
        buffer = self.inputs['in'].read(offset, duration)
        print(buffer)
        return buffer
