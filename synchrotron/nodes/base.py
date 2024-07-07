from __future__ import annotations

import abc
from dataclasses import dataclass
from typing import TYPE_CHECKING, get_type_hints

if TYPE_CHECKING:
    from ..types import SignalBuffer


class Port:
    def __init__(self, node: Node, name: str) -> None:
        self.node = node
        self.name = name
        self.buffer: SignalBuffer | None = None

    @property
    def class_name(self) -> str:
        return self.node.__class__.__name__ + '.' + self.name

    @property
    def instance_name(self) -> str:
        return self.node.name + '.' + self.name

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} {self.node.__class__.__name__} {self.instance_name!r}>'


class Input(Port):
    def read(self) -> SignalBuffer:
        if self.buffer is None:
            raise RuntimeError('input buffer cannot be read from as it is empty')
        return self.buffer


class Output(Port):
    def write(self, buffer: SignalBuffer) -> None:
        self.buffer = buffer


class Connection:
    def __init__(self, source: Output, sink: Input) -> None:
        self.source = source
        self.sink = sink

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} {self.source.instance_name!r} -> {self.sink.instance_name!r}>'


class Node(abc.ABC):
    def __init__(self, name: str) -> None:
        self.name = name
        self.inputs: dict[str, Input] = {}
        self.outputs: dict[str, Output] = {}

        # A bit of magic so inputs and outputs are nicer to interact with
        for name, cls in get_type_hints(self.__class__).items():
            if cls is Input:
                instance = Input(self, name=name)
                self.inputs[name] = instance
                setattr(self, name, instance)
            elif cls is Output:
                instance = Output(self, name=name)
                self.outputs[name] = instance
                setattr(self, name, instance)

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} {self.name!r} ({len(self.inputs)} => {len(self.outputs)})>'

    @abc.abstractmethod
    def render(self, ctx: RenderContext) -> None:
        pass


@dataclass
class RenderContext:
    global_clock: int
    sample_rate: int
    buffer_size: int
