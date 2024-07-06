from __future__ import annotations

import threading
from queue import SimpleQueue
from typing import TYPE_CHECKING

import pyaudio
from graphlib import TopologicalSorter

from . import nodes
from .console.app import Console
from .nodes.base import RenderContext

if TYPE_CHECKING:
    from queue import Queue

    from .nodes import Input, Node, Output


class Synchrotron:
    def __init__(self, sample_rate: int = 44100, buffer_size: int = 256):
        self.pyaudio_session = pyaudio.PyAudio()
        self.global_clock = 0
        self.nodes: dict[Node, set[Node]] = {}
        self.connections: dict[Output, set[Input]] = {}
        self.pending_connections: SimpleQueue[tuple[Output, Input, bool]] = SimpleQueue()
        self.output_queues: list[Queue] = []
        self.stop_event = threading.Event()

        # It'd be cool to have a dynamic sample rate and buffer size, but it would be such an implementation headache
        self.sample_rate = sample_rate
        self.buffer_size = buffer_size

    def add_node(self, node: Node):
        if node in self.nodes:
            return

        self.nodes[node] = set()
        for output in node.outputs.values():
            self.connections[output] = set()

    def connect(self, from_output: Output, to_input: Input):
        self.pending_connections.put((from_output, to_input, True))

    def disconnect(self, from_output: Output, to_input: Input):
        self.pending_connections.put((from_output, to_input, False))

    def add_output_queue(self, queue: Queue):
        self.output_queues.append(queue)

    def apply_pending_connections(self) -> None:
        while not self.pending_connections.empty():
            source, destination, connect = self.pending_connections.get()
            if connect:
                self.nodes[destination.node].add(source.node)
                self.connections[source].add(destination)
            else:
                self.connections[source].remove(destination)
                if not any(
                    self.connections[output].intersection(destination.node.inputs.values())
                    for output in source.node.outputs.values()
                ):
                    self.nodes[destination.node].remove(source.node)

    def render_graph(self) -> bool:
        self.apply_pending_connections()

        if self.stop_event.is_set():
            return False

        render_context = RenderContext(
            global_clock=self.global_clock,
            sample_rate=self.sample_rate,
            buffer_size=self.buffer_size
        )
        node_graph = TopologicalSorter(self.nodes)
        for node in node_graph.static_order():
            node.render(render_context)
            for output in node.outputs.values():
                for target_input in self.connections[output]:
                    target_input.buffer = output.buffer

        for queue in self.output_queues:
            queue.join()
        self.global_clock += 1
        return True

    def run(self) -> None:
        while self.render_graph():
            pass

    def stop(self) -> None:
        self.stop_event.set()
        self.pyaudio_session.terminate()
        for queue in self.output_queues:
            try:
                while True:
                    queue.task_done()
            except ValueError:  # noqa: PERF203
                pass


def init_nodes(synchrotron: Synchrotron) -> None:
    low = nodes.data.ConstantNode(440)
    high = nodes.data.ConstantNode(500)
    modulator = nodes.data.UniformRandomNode()
    source = nodes.audio.SineNode()
    sink = nodes.audio.PlaybackNode(synchrotron)
    # debug = nodes.data.DebugNode()
    for node in (low, high, modulator, source, sink):
        synchrotron.add_node(node)

    synchrotron.connect(low.out, modulator.min)
    synchrotron.connect(high.out, modulator.max)
    synchrotron.connect(modulator.out, source.frequency)
    synchrotron.connect(source.out, sink.left)
    synchrotron.connect(source.out, sink.right)
    # synchrotron.connect(source.out, debug.input)


if __name__ == '__main__':
    session = Synchrotron()
    init_nodes(session)
    render_thread = threading.Thread(target=session.run, name='RenderThread')
    render_thread.start()
    try:
        Console(session).run()
    finally:
        session.stop()
