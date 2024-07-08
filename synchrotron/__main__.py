from __future__ import annotations

import threading
from typing import TYPE_CHECKING

import lark
import pyaudio
from graphlib import TopologicalSorter

import synchrolang

from . import nodes
from .console.app import Console
from .nodes.base import Connection, Input, Output, RenderContext

if TYPE_CHECKING:
    from queue import Queue

    from .nodes import Node, Port


@lark.v_args(inline=True)
class SynchrolangTransformer(lark.Transformer):
    def __init__(self, synchrotron: Synchrotron) -> None:
        super().__init__()
        self.synchrotron = synchrotron

    def node(self, name: lark.Token) -> Node:
        return self.synchrotron.get_node(name)

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


class Synchrotron:
    def __init__(self, sample_rate: int = 44100, buffer_size: int = 256) -> None:
        self.pyaudio_session = pyaudio.PyAudio()
        self.global_clock = 0
        self.stop_event = threading.Event()
        self.synchrolang_transformer = SynchrolangTransformer(self)

        # It'd be cool to have a dynamic sample rate and buffer size, but it would be such an implementation headache
        self.sample_rate = sample_rate
        self.buffer_size = buffer_size

        self._nodes: list[Node] = []
        self._node_dependencies: dict[Node, set[Node]] = {}
        self._connections: list[Connection] = []
        self._output_queues: list[Queue] = []

    def get_node(self, node_name: str) -> Node:
        try:
            return next(node for node in self._nodes if node.name == node_name)
        except StopIteration:
            raise ValueError(f"node '{node_name}' not found") from None

    def add_node(self, node: Node) -> None:
        if node in self._nodes:
            raise ValueError(f'node {node!r} already added to graph')
        name_collision = next((graph_node for graph_node in self._nodes if graph_node.name == node.name), None)
        if name_collision is not None:
            raise ValueError(f'node {node!r} has a duplicate name with node {name_collision.name}')

        self._nodes.append(node)
        self._node_dependencies[node] = set()

    def get_connection(self, source: Output, sink: Input, return_disconnected: bool = False) -> Connection:
        for connection in self._connections:
            if connection.source == source and connection.sink == sink:
                return connection

        if return_disconnected:
            return Connection(source, sink)
        raise ValueError(f'connection {source.instance_name} -> {sink.instance_name} does not exist')

    def add_connection(self, source: Output, sink: Input) -> None:
        connection = self.get_connection(source, sink, return_disconnected=True)
        if connection.is_connected:
            return

        connection.is_connected = True
        source.connections.append(connection)
        sink.connection = connection
        self._connections.append(connection)

        self._node_dependencies[sink.node].add(source.node)

    def remove_connection(self, source: Output, sink: Input) -> None:
        try:
            connection = self.get_connection(source, sink)
        except ValueError:
            return

        connection.is_connected = False
        source.connections.remove(connection)
        sink.connection = None
        self._connections.remove(connection)

        # If sink node has no inputs connected to source node outputs then remove node dependency
        if not any(input_port.connection.source.node == source for input_port in sink.node.inputs):
            self._node_dependencies[sink.node].remove(source.node)

    def execute(self, synchrolang_expression: str) -> Node | Port | Connection | lark.Token:
        tree = synchrolang.parser.parse(synchrolang_expression)
        return self.synchrolang_transformer.transform(tree)

    def add_output_queue(self, queue: Queue) -> None:
        self._output_queues.append(queue)

    def render_graph(self) -> bool:
        if self.stop_event.is_set():
            return False

        render_context = RenderContext(
            global_clock=self.global_clock,
            sample_rate=self.sample_rate,
            buffer_size=self.buffer_size
        )
        node_graph = TopologicalSorter(self._node_dependencies)
        for node in node_graph.static_order():
            node.render(render_context)
            for output in node.outputs:
                for connection in output.connections:
                    connection.sink.buffer = connection.source.buffer

        for queue in self._output_queues:
            queue.join()
        self.global_clock += 1
        return True

    def run(self) -> None:
        while self.render_graph():
            pass

    def stop(self) -> None:
        self.stop_event.set()
        self.pyaudio_session.terminate()
        for queue in self._output_queues:
            try:
                while True:
                    queue.task_done()
            except ValueError:  # noqa: PERF203
                pass


def init_nodes(synchrotron: Synchrotron) -> None:
    low = nodes.data.ConstantNode('low', 440)
    high = nodes.data.ConstantNode('high', 880)
    modulator = nodes.data.UniformRandomNode('modulator')
    source = nodes.audio.SineNode('source')
    sink = nodes.audio.PlaybackNode('sink', synchrotron)
    for node in (low, high, modulator, source, sink):
        synchrotron.add_node(node)

    synchrotron.add_connection(low.out, modulator.min)
    synchrotron.add_connection(high.out, modulator.max)
    synchrotron.add_connection(modulator.out, source.frequency)
    synchrotron.add_connection(source.out, sink.left)
    synchrotron.add_connection(source.out, sink.right)


if __name__ == '__main__':
    session = Synchrotron(buffer_size=22050)
    init_nodes(session)
    render_thread = threading.Thread(target=session.run, name='RenderThread')
    render_thread.start()
    try:
        Console(session).run()
    finally:
        session.stop()
