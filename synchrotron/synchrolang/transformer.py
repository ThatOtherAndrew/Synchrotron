from __future__ import annotations

import random
import string
from types import NoneType
from typing import TYPE_CHECKING, Any, TypeAlias

import lark

from synchrotron.nodes import Connection, Input, Node, Output, Port
from synchrotron.nodes.core import DataNode

if TYPE_CHECKING:
    from threading import Thread

    from synchrotron.synchrotron import Synchrotron

Value: TypeAlias = str | int | float | list['Value'] | bool | None
Expression: TypeAlias = Value | type[Node] | Node | Port | Connection


@lark.v_args(inline=True)
class SynchrolangTransformer(lark.Transformer):
    def __init__(self, synchrotron: Synchrotron) -> None:
        super().__init__()
        self.synchrotron = synchrotron

    # Literal values

    int = int
    float = float
    string = str

    @staticmethod
    def bool(token: lark.Token) -> bool:
        return token.lower() == 'true'

    @staticmethod
    def array(*elements: Value) -> list[Value]:
        return list(elements)

    none = NoneType

    def global_var(self, name: lark.Token) -> Any:
        global_vars = {
            'synchrotron': self.synchrotron,
            'pyaudio': self.synchrotron.pyaudio_session,
            'clock': self.synchrotron.global_clock,
            'thread': self.synchrotron.render_thread,
            'rate': self.synchrotron.sample_rate,
            'buffer': self.synchrotron.buffer_size,
            'nodes': self.synchrotron.nodes,
        }

        return_obj = global_vars.get(name, ...)
        if return_obj is ...:
            raise ValueError(f"unknown global variable '{name}'")
        return return_obj

    # Node instantiation

    def node_type(self, type_name: lark.Token) -> type[Node]:
        return self.synchrotron.get_node_type(type_name)

    @staticmethod
    def arguments(*args: Value) -> list[Value]:
        return list(args)

    @staticmethod
    def keyword_arguments(*args: lark.Token | Value) -> dict[str, Value]:
        return dict(zip((key.value for key in args[0::2]), args[1::2]))

    # Graph elements

    def node(self, node_name: lark.Token) -> Node:
        return self.synchrotron.get_node(node_name)

    @staticmethod
    def port(node: Node, port_name: lark.Token) -> Port:
        return node.get_port(port_name)

    @staticmethod
    def input(port: Port) -> Input:
        if isinstance(port, Input):
            return port

        raise ValueError(f"'{port.instance_name}' is an output port ({port.type_name}) and cannot be used as an input")

    @staticmethod
    def output(port: Port) -> Output:
        if isinstance(port, Output):
            return port

        raise ValueError(f"'{port.instance_name}' is an input port ({port.type_name}) and cannot be used as an output")

    def connection(self, source: Output, sink: Input) -> Connection:
        return self.synchrotron.get_connection(source, sink, return_disconnected=True)

    # Commands

    def start(self) -> Thread:
        return self.synchrotron.start_rendering()

    def stop(self) -> None:
        self.synchrotron.stop_rendering()

    def export(self) -> str:
        return self.synchrotron.export_state()

    def create(self, cls: type[Node] | int | float, name: str | None = None) -> Node:
        if name is None:
            existing_names = {node.name for node in self.synchrotron.nodes}
            while name is None or name in existing_names:
                name = '_' + ''.join(random.choice(string.ascii_lowercase) for _ in range(5))
        else:
            name = str(name)

        if isinstance(cls, type):
            node = cls(synchrotron=self.synchrotron, name=name)
        else:
            node = DataNode(synchrotron=self.synchrotron, name=name, value=cls)

        self.synchrotron.add_node(node)
        return node

    def link(self, connection: Connection) -> Connection:
        return self.synchrotron.add_connection(connection.source, connection.sink)

    def unlink(self, target: Node | Port | Connection) -> str:
        if isinstance(target, Node):
            unlinked_count = len(self.synchrotron.unlink_node(target))
        elif isinstance(target, Port):
            unlinked_count = len(self.synchrotron.unlink_port(target))
        elif isinstance(target, Connection):
            unlinked_count = int(bool(self.synchrotron.remove_connection(target.source, target.sink)))
        else:
            raise TypeError(f'invalid target to unlink: expected Node | Port | Connection, got {type(target)}')

        return f'{unlinked_count} connection{"s" if unlinked_count != 1 else ""} unlinked'

    def remove(self, node: Node) -> Node:
        return self.synchrotron.remove_node(node.name)

    @staticmethod
    def script(*commands: Any) -> tuple[Any, ...]:
        return commands
