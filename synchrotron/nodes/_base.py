from __future__ import annotations

import abc
from dataclasses import dataclass
from importlib import import_module
from pathlib import Path
from typing import TYPE_CHECKING, Any, get_type_hints

import numpy as np

if TYPE_CHECKING:
    from collections.abc import ValuesView

    from numpy.typing import NDArray

    from synchrotron.synchrotron import Synchrotron


class Port:
    def __init__(self, node: Node, name: str) -> None:
        self.node = node
        self.name = name
        self.buffer: Any = None

    @property
    def type_name(self) -> str:
        return self.node.__class__.__name__ + '.' + self.name

    @property
    def instance_name(self) -> str:
        return self.node.name + '.' + self.name

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} {self.node.__class__.__name__} {self.instance_name!r}>'

    def as_json(self) -> dict:
        return {
            'node_name': self.node.name,
            'port_name': self.name,
        }


class Input(Port, abc.ABC):
    def __init__(self, node: Node, name: str) -> None:
        super().__init__(node=node, name=name)
        self.connection: Connection | None = None

    @abc.abstractmethod
    def read(self, *_, **__) -> Any:
        return self.buffer

    def as_json(self, include_source: bool = True) -> dict:
        json = super().as_json()
        json['type'] = self.__class__.__name__
        if include_source:
            json['source'] = None if self.connection is None else self.connection.source.as_json(include_sinks=False)
        return json


class Output(Port, abc.ABC):
    def __init__(self, node: Node, name: str) -> None:
        super().__init__(node=node, name=name)
        self.connections: list[Connection] = []

    @abc.abstractmethod
    def write(self, buffer: Any) -> None:
        self.buffer = buffer

    def as_json(self, include_sinks: bool = True) -> dict:
        json = super().as_json()
        json['type'] = self.__class__.__name__
        if include_sinks:
            json['sinks'] = [conn.sink.as_json(include_source=False) for conn in self.connections]
        return json


class DataInput(Input):
    def read(self, default: Any = None) -> Any:
        if self.buffer is None:
            return default
        return self.buffer


class DataOutput(Output):
    def write(self, buffer: Any) -> None:
        self.buffer = buffer


class StreamInput(Input):
    # TODO: Some magic with generics to allow for non-float32 streams
    def read(self, render_context: RenderContext, default_constant: float = 0.) -> NDArray[np.float32]:
        if self.connection is None:
            self.buffer = np.full(shape=render_context.buffer_size, fill_value=default_constant, dtype=np.float32)
        elif not isinstance(self.buffer, np.ndarray):
            self.buffer = np.full(shape=render_context.buffer_size, fill_value=self.buffer, dtype=np.float32)

        return self.buffer


class StreamOutput(Output):
    def write(self, buffer: NDArray[np.float32]) -> None:
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

    def as_json(self, connection_assertion: bool | None = None) -> dict:
        if connection_assertion is not None and connection_assertion != self.is_connected:
            raise RuntimeError(f'connection state assertion failed '
                               f'(is_connected is {self.is_connected}, expected {connection_assertion})')

        return {
            'source': self.source.as_json(include_sinks=False),
            'sink': self.sink.as_json(include_source=False),
        }


class Node(abc.ABC):
    def __init__(self, synchrotron: Synchrotron, name: str) -> None:
        self.synchrotron = synchrotron
        self.name = name
        self.exports: dict[str, Any] = {}
        self._inputs: dict[str, Input] = {}
        self._outputs: dict[str, Output] = {}

        # A bit of magic so inputs and outputs are nicer to interact with
        for name, cls in get_type_hints(self.__class__).items():
            if not issubclass(cls, Port):
                continue

            if name in self._inputs or name in self._outputs:
                raise RuntimeError(f"duplicate port name '{name}' for node {self.__class__.__name__}")

            if issubclass(cls, Input):
                instance = cls(self, name=name)
                self._inputs[name] = instance
            elif issubclass(cls, Output):
                instance = cls(self, name=name)
                self._outputs[name] = instance
            else:
                raise RuntimeError(f"unrecognised port type '{cls.__name__}'")

            setattr(self, name, instance)

    def __repr__(self) -> str:
        parts = [
            self.__class__.__name__,
            repr(self.name),
            f'({len(self._inputs)} => {len(self._outputs)})',
        ]
        if self.exports:
            parts.append('{' + ', '.join(f'{key}: {value!r}' for key, value in self.exports.items()) + '}')

        return f'<{" ".join(parts)}>'

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

    def as_json(self) -> dict:
        return {
            'name': self.name,
            'type': self.__class__.__name__,
            'inputs': [input_port.as_json() for input_port in self.inputs],
            'outputs': [output_port.as_json() for output_port in self.outputs],
            'exports': self.exports,
        }

    def teardown(self) -> None:  # noqa: B027
        pass


@dataclass
class RenderContext:
    global_clock: int
    sample_rate: int
    buffer_size: int


def get_node_types() -> list[type[Node]]:
    node_types = []

    for path in Path(__file__).parent.rglob('[!_]*.py'):
        module = import_module('.' + path.stem, package='synchrotron.nodes')
        if hasattr(module, '__all__'):
            node_types.extend(getattr(module, node_name) for node_name in module.__all__)

    return node_types
