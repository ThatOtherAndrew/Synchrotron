from __future__ import annotations

from synchrotron.nodes import Input, Node, Output


class Message:
    OPCODE_MASK = 0xf0
    CHANNEL_MASK = 0x0f

    NOTE_OFF = 0x70
    NOTE_ON = 0x80


class MidiBuffer:
    def __init__(self, length: int):
        self.data: dict[int, list[bytes]] = {}
        self.length = length

    def __len__(self) -> int:
        return sum(len(msgs) for msgs in self.data.values())

    def get_messages_at_pos(self, position: int) -> tuple[bytes, ...]:
        if position not in range(self.length):
            raise ValueError(f'MIDI message position {position} out of bounds for buffer length {self.length}')

        if position not in self.data:
            return ()
        return tuple(self.data[position])

    def add_message(self, position: int, message: bytes):
        if position not in range(self.length):
            raise ValueError(f'MIDI message position {position} out of bounds for buffer length {self.length}')

        if position not in self.data:
            self.data[position] = []
        self.data[position].append(message)

    def __repr__(self) -> str:
        return f'MidiBuffer({self.data})'


class MidiInput(Input):
    def __init__(self, node: Node, name: str) -> None:
        super().__init__(node, name)
        self.buffer: MidiBuffer = MidiBuffer(length=node.synchrotron.buffer_size)

    def read(self) -> MidiBuffer:
        return self.buffer


class MidiOutput(Output):
    def __init__(self, node: Node, name: str):
        super().__init__(node, name)
        self.buffer: MidiBuffer = MidiBuffer(length=node.synchrotron.buffer_size)

    def write(self, buffer: MidiBuffer) -> None:
        self.buffer = buffer
