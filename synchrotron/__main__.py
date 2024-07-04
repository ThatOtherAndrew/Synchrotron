from queue import SimpleQueue
from time import sleep

import pyaudio
from graphlib import TopologicalSorter

from . import nodes
from .nodes import Input, Node, Output
from .nodes.base import RenderContext


class Synchrotron:
    def __init__(self, sample_rate: int = 44100, buffer_size: int = 44100):
        self.pyaudio_session = pyaudio.PyAudio()
        self.global_clock = 0
        self.nodes: dict[Node, set[Node]] = {}
        self.connections: dict[Output, set[Input]] = {}
        self.pending_connections: SimpleQueue[tuple[Output, Input, bool]] = SimpleQueue()

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

    def tick(self):
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

        self.global_clock += 1

    def stop(self) -> None:
        self.pyaudio_session.terminate()


def main(synchrotron: Synchrotron) -> None:
    low = nodes.data.ConstantNode(440)
    high = nodes.data.ConstantNode(880)
    modulator = nodes.data.UniformRandomNode()
    source = nodes.audio.SineNode()
    sink = nodes.audio.PlaybackNode(synchrotron)
    debug = nodes.data.DebugNode()
    for node in (low, high, modulator, source, sink, debug):
        synchrotron.add_node(node)

    synchrotron.connect(low.out, modulator.min)
    synchrotron.connect(high.out, modulator.max)
    synchrotron.connect(modulator.out, source.frequency)
    synchrotron.connect(source.out, sink.left)
    synchrotron.connect(source.out, sink.right)
    synchrotron.connect(source.out, debug.input)

    while True:
        print(f'\rTick {synchrotron.global_clock}', end='')
        synchrotron.tick()


if __name__ == '__main__':
    session = Synchrotron()
    try:
        main(session)
        sleep(0.5)
    except KeyboardInterrupt:
        print('\nKeyboard interrupt received, exiting')
    finally:
        session.stop()
