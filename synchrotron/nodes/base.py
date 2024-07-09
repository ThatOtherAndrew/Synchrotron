from __future__ import annotations

import abc
from dataclasses import dataclass
from typing import TYPE_CHECKING, get_type_hints

import numpy as np

if TYPE_CHECKING:
    from collections.abc import ValuesView

    from ..__main__ import Synchrotron
    from ..types import SignalBuffer


class Port:
    def __init__(self, node: Node, name: str) -> None:
        self.node = node
        self.name = name
        self.buffer: SignalBuffer = np.zeros(shape=1, dtype=np.float32)

    @property
    def class_name(self) -> str:
        return self.node.__class__.__name__ + '.' + self.name

    @property
    def instance_name(self) -> str:
        return self.node.name + '.' + self.name

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} {self.node.__class__.__name__} {self.instance_name!r}>'


class Input(Port):
    def __init__(self, node: Node, name: str) -> None:
        super().__init__(node=node, name=name)
        self.connection: Connection | None = None

    def read(self, render_context: RenderContext) -> SignalBuffer:
        if self.connection is None:
            self.buffer = np.zeros(shape=render_context.buffer_size, dtype=np.float32)
        return self.buffer


class Output(Port):
    def __init__(self, node: Node, name: str) -> None:
        super().__init__(node=node, name=name)
        self.connections: list[Connection] = []

    def write(self, buffer: SignalBuffer) -> None:
        self.buffer = buffer


class Connection:
    def __init__(self, source: Output, sink: Input, is_connected: bool = False) -> None:
        self.source = source
        self.sink = sink
        self.is_connected = is_connected

    def __repr__(self) -> str:
        status = 'connected' if self.is_connected else 'disconnected'
        return f'<{self.__class__.__name__} {self.source.instance_name!r} -> {self.sink.instance_name!r} ({status})>'

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            raise TypeError(f"cannot compare instances of '{self.__class__.__name__}' and '{other.__class__.__name__}'")
        return self.source == other.source and self.sink == other.sink


class Node(abc.ABC):
    def __init__(self, synchrotron: Synchrotron, name: str) -> None:
        self.synchrotron = synchrotron
        self.name = name
        self._inputs: dict[str, Input] = {}
        self._outputs: dict[str, Output] = {}

        # A bit of magic so inputs and outputs are nicer to interact with
        for name, cls in get_type_hints(self.__class__).items():
            if cls not in (Input, Output):
                continue

            if name in self._inputs or name in self._outputs:
                raise RuntimeError(f"duplicate port name '{name}' for node {self.__class__.__name__}")

            if cls is Input:
                instance = Input(self, name=name)
                self._inputs[name] = instance
            else:
                instance = Output(self, name=name)
                self._outputs[name] = instance

            setattr(self, name, instance)

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} {self.name!r} ({len(self._inputs)} => {len(self._outputs)})>'

    @property
    def inputs(self) -> ValuesView[Input]:
        return self._inputs.values()

    @property
    def outputs(self) -> ValuesView[Output]:
        return self._outputs.values()

    def get_input(self, input_name: str) -> Input:
        if input_name in self._inputs:
            return self._inputs[input_name]
        raise ValueError(f'input {self.__class__.__name__}.{input_name} does not exist')

    def get_output(self, output_name: str) -> Output:
        if output_name in self._outputs:
            return self._outputs[output_name]
        raise ValueError(f'output {self.__class__.__name__}.{output_name} does not exist')

    def get_port(self, port_name: str) -> Port:
        if port_name in self._inputs:
            return self._inputs[port_name]
        if port_name in self._outputs:
            return self._outputs[port_name]
        raise ValueError(f'port {self.__class__.__name__}.{port_name} does not exist')

    @abc.abstractmethod
    def render(self, ctx: RenderContext) -> None:
        pass


@dataclass
class RenderContext:
    global_clock: int
    sample_rate: int
    buffer_size: int
