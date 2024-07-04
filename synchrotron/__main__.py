from queue import SimpleQueue

import pyaudio
from graphlib import TopologicalSorter

from .nodes import Input, Node, Output


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
                self.nodes[source.node].add(destination.node)
                self.connections[source].add(destination)
            else:
                self.connections[source].remove(destination)
                if not any(
                    self.connections[output].intersection(destination.node.inputs.values())
                    for output in source.node.outputs.values()
                ):
                    self.nodes[source.node].remove(destination.node)

        node_graph = TopologicalSorter(self.nodes)
        node_graph.prepare()
        while node_graph.is_active():
            for node in node_graph.get_ready():
                node.render()
                for output in node.outputs.values():
                    for target_input in self.connections[output]:
                        target_input.buffer = output.buffer
                node_graph.done(node)


if __name__ == '__main__':
    ...
