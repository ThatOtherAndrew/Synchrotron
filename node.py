from collections.abc import Callable
from functools import partial
from typing import Any


class Node:
    def __init__(self) -> None:
        self.inputs: dict[str, Input] = {}
        self.outputs: dict[str, Output] = {}

    def render(self, offset: int, duration: int) -> None:
        for output in self.outputs.values():
            output.render(offset, duration)


class Input:
    def __init__(self, node: Node) -> None:
        self.node = node


class Output:
    def __init__(self, node: Node, func: Callable[[int, int], Any]) -> None:
        self.node = node
        self.func = func
        self.buffer: Any = None

    def render(self, offset: int, duration: int) -> None:
        self.buffer = self.func(offset, duration)


class AudioPassthroughNode(Node):
    def __init__(self) -> None:
        super().__init__()
        self.inputs['in'] = Input(self)
        self.outputs['out'] = Output(self, partial(self.out, self))

    def out(self, offset: int, duration: int):
        buffer = self.inputs[]
