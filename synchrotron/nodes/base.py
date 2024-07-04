from __future__ import annotations

import abc
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..types import SignalBuffer


class Input:
    def __init__(self, node: Node) -> None:
        self.node = node
        self.buffer: SignalBuffer | None = None

    def __repr__(self) -> str:
        return f'<{self.node.__class__.__name__} input>'

    def read(self) -> SignalBuffer:
        if self.buffer is None:
            raise RuntimeError('input buffer cannot be read from as it is empty')
        return self.buffer


class Output:
    def __init__(self, node: Node) -> None:
        self.node = node
        self.buffer = None

    def __repr__(self) -> str:
        return f'<{self.node.__class__.__name__} output>'

    def write(self, buffer: SignalBuffer) -> None:
        self.buffer = buffer


class Node(abc.ABC):
    def __init__(self) -> None:
        self.inputs: dict[str, Input] = {}
        self.outputs: dict[str, Output] = {}

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} (I:{len(self.inputs)} O:{len(self.outputs)})>'

    @abc.abstractmethod
    def render(self, ctx: RenderContext) -> None:
        pass


@dataclass
class RenderContext:
    global_clock: int
    sample_rate: int
    buffer_size: int
