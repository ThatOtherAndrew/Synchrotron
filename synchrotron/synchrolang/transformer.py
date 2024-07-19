from __future__ import annotations

from types import NoneType
from typing import TYPE_CHECKING, Any, TypeAlias

import lark

from synchrotron import nodes
from synchrotron.nodes import Connection, Input, Node, Output, Port

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

    @staticmethod
    def node_class(class_name: lark.Token) -> type[Node]:
        node = getattr(nodes, class_name, NoneType)
        if not issubclass(node, Node):
            raise ValueError(f"node class '{class_name}' not found")

        return node

    @staticmethod
    def arguments(*args: Value) -> list[Value]:
        return list(args)

    @staticmethod
    def keyword_arguments(*args: lark.Token | Value) -> dict[str, Value]:
        return dict(zip((key.value for key in args[0::2]), args[1::2]))

    def node_init(
        self,
        name: lark.Token,
        cls: type[Node],
        args: list[Value],
        kwargs: dict[str, Value],
    ) -> Node:
        # noinspection PyArgumentList
        node = cls(self.synchrotron, str(name), *args, **kwargs)
        self.synchrotron.add_node(node)
        return node

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

        raise ValueError(f"'{port.instance_name}' is an output port ({port.class_name}) and cannot be used as an input")

    @staticmethod
    def output(port: Port) -> Output:
        if isinstance(port, Output):
            return port

        raise ValueError(f"'{port.instance_name}' is an input port ({port.class_name}) and cannot be used as an output")

    def connection(self, source: Output, sink: Input) -> Connection:
        return self.synchrotron.get_connection(source, sink, return_disconnected=True)

    # Commands

    def start(self) -> Thread:
        return self.synchrotron.start_rendering()

    def stop(self) -> None:
        self.synchrotron.stop_rendering()

    @staticmethod
    def create(node: Node) -> Node:
        return node

    def link(self, connection: Connection) -> Connection:
        return self.synchrotron.add_connection(connection.source, connection.sink)

    def unlink(self, target: Node | Port | Connection) -> str:
        ports: list[Port] = []
        connections = []
        unlinks = 0

        if isinstance(target, Node):
            ports.extend(target.inputs)
            ports.extend(target.outputs)
        elif isinstance(target, Port):
            ports.append(target)
        elif isinstance(target, Connection):
            connections.append(target)
        else:
            raise TypeError(f'invalid target to unlink: expected Node | Port | Connection, got {type(target)}')

        for port in ports:
            if isinstance(port, Input):
                if port.connection is not None:
                    connections.append(port.connection)
            elif isinstance(port, Output):
                connections.extend(port.connections)

        for connection in connections:
            if self.synchrotron.get_connection(connection.source, connection.sink).is_connected:
                self.synchrotron.remove_connection(connection.source, connection.sink)
                unlinks += 1

        return f'{unlinks} connection{"s" if unlinks != 1 else ""} unlinked'

    def remove(self, node: Node) -> Node:
        return self.synchrotron.remove_node(node.name)

    @staticmethod
    def script(*commands: Any) -> tuple[Any, ...]:
        return commands
