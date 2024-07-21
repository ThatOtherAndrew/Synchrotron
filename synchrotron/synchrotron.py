from __future__ import annotations

from threading import Event, Thread
from typing import TYPE_CHECKING, Any

from graphlib import TopologicalSorter
from pyaudio import PyAudio

from . import synchrolang
from .nodes import Connection, Input, Node, Output, Port, RenderContext

if TYPE_CHECKING:
    from queue import Queue


class Synchrotron:
    def __init__(self, sample_rate: int = 44100, buffer_size: int = 256) -> None:
        self.pyaudio_session = PyAudio()
        self.global_clock = 0
        self.stop_event = Event()
        self.render_thread: Thread | None = None
        self.synchrolang_parser = synchrolang.SynchrolangParser()
        self.synchrolang_transformer = synchrolang.SynchrolangTransformer(self)

        # It'd be cool to have a dynamic sample rate and buffer size, but it would be such an implementation headache
        self.sample_rate = sample_rate
        self.buffer_size = buffer_size

        self.nodes: list[Node] = []
        self.connections: list[Connection] = []
        self._node_dependencies: dict[Node, set[Node]] = {}
        self._output_queues: list[Queue] = []

    def get_node(self, node_name: str) -> Node:
        try:
            return next(node for node in self.nodes if node.name == node_name)
        except StopIteration:
            raise ValueError(f"node '{node_name}' not found") from None

    def add_node(self, node: Node) -> None:
        if node in self.nodes:
            raise ValueError(f'node {node!r} already added to graph')
        name_collision = next((graph_node for graph_node in self.nodes if graph_node.name == node.name), None)
        if name_collision is not None:
            raise ValueError(f'node {node!r} has a duplicate name with node {name_collision.name}')

        self.nodes.append(node)
        self._node_dependencies[node] = set()

    def remove_node(self, node_name: str) -> Node:
        node = self.get_node(node_name)

        # Detatch node from graph to prepare for removal
        for input_port in node.inputs:
            if input_port.connection is not None:
                self.remove_connection(input_port.connection.source, input_port)
        for output_port in node.outputs:
            for connection in output_port.connections:
                self.remove_connection(output_port, connection.sink)

        self.nodes.remove(node)
        self._node_dependencies.pop(node, None)

        return node

    def get_connection(self, source: Output, sink: Input, return_disconnected: bool = False) -> Connection:
        for connection in self.connections:
            if connection.source == source and connection.sink == sink:
                return connection

        if return_disconnected:
            return Connection(source, sink)
        raise ValueError(f'connection {source.instance_name} -> {sink.instance_name} does not exist')

    def add_connection(self, source: Output, sink: Input, strict: bool = False) -> Connection:
        connection = self.get_connection(source, sink, return_disconnected=True)
        if connection.is_connected:
            return connection

        if sink.connection is not None:
            if strict:
                raise ValueError(f'output {sink.instance_name} is already connected')
            self.remove_connection(sink.connection.source, sink)

        connection.is_connected = True
        source.connections.append(connection)
        sink.connection = connection
        self.connections.append(connection)
        self._node_dependencies[sink.node].add(source.node)

        return connection

    def remove_connection(self, source: Output, sink: Input) -> Connection | None:
        try:
            connection = self.get_connection(source, sink)
        except ValueError:
            return None

        connection.is_connected = False
        source.connections.remove(connection)
        sink.connection = None
        self.connections.remove(connection)

        # If sink node has no inputs connected to source node outputs then remove node dependency
        if not any(
            input_port.connection.source.node == source.node
            for input_port in sink.node.inputs
            if input_port.connection is not None
        ):
            self._node_dependencies[sink.node].remove(source.node)

        return connection

    def unlink_port(self, port: Port) -> list[Connection]:
        if isinstance(port, Input):
            removed_connections = [self.remove_connection(port.connection.source, port.connection.sink)]
        else:
            port: Output
            removed_connections = [
                self.remove_connection(connection.source, connection.sink)
                for connection in port.connections
            ]

        return list(filter(None, removed_connections))

    def unlink_node(self, node: Node) -> list[Connection]:
        removed_connections = []
        for port in (*node.inputs, *node.outputs):
            removed_connections.extend(self.unlink_port(port))

        return removed_connections

    def execute(self, script: str) -> tuple[Any, ...]:
        tree = self.synchrolang_parser.parse(script)
        return self.synchrolang_transformer.transform(tree)

    def add_output_queue(self, queue: Queue) -> None:
        self._output_queues.append(queue)

    def render_graph(self) -> None:
        render_context = RenderContext(
            global_clock=self.global_clock,
            sample_rate=self.sample_rate,
            buffer_size=self.buffer_size,
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

    def start_rendering(self) -> Thread:
        if self.render_thread is not None and self.render_thread.is_alive():
            raise RuntimeError('render thread is already running')
        self.stop_event.clear()

        def render_loop() -> None:
            while not self.stop_event.is_set():
                self.render_graph()

        self.render_thread = Thread(target=render_loop, name='RenderThread')
        self.render_thread.start()
        return self.render_thread

    def stop_rendering(self) -> None:
        self.stop_event.set()
        if self.render_thread is not None:
            self.render_thread.join()

    def shutdown(self) -> None:
        self.stop_rendering()
        self.pyaudio_session.terminate()
