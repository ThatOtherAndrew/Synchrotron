from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
from rtmidi import MidiIn

from . import DataInput, Message, MidiBuffer, MidiInput, MidiOutput, Node, RenderContext, StreamOutput

if TYPE_CHECKING:
    from synchrotron.synchrotron import Synchrotron

__all__ = ['MidiInputNode', 'MonophonicRenderNode']


class MidiInputNode(Node):
    port: DataInput
    out: MidiOutput

    def __init__(self, synchrotron: Synchrotron, name: str):
        super().__init__(synchrotron, name)

        self.current_port = self.port.read()
        self.midi_in = MidiIn().open_port(self.current_port)
        self.last_message_time: int | None = None

        self.exports['Port Count'] = self.midi_in.get_port_count()
        self.exports['Selected Port'] = self.midi_in.get_port_name()

    def render(self, ctx: RenderContext) -> None:
        if (new_port := self.port.read()) != self.current_port:
            self.midi_in.close_port()
            self.midi_in.open_port(new_port)
            self.last_message_time = None

        buffer = MidiBuffer(length=ctx.buffer_size)

        while message := self.midi_in.get_message():
            # https://spotlightkid.github.io/python-rtmidi/rtmidi.html#rtmidi.MidiIn.get_message
            message: tuple[list[int], float]

            buffer.add_message(position=0, message=bytes(message[0]))

        self.out.write(buffer)


class MonophonicRenderNode(Node):
    midi: MidiInput
    frequency: StreamOutput

    def __init__(self, synchrotron: Synchrotron, name: str):
        super().__init__(synchrotron, name)
        self.current_note = 0

    def render(self, ctx: RenderContext) -> None:
        output = np.empty(shape=ctx.buffer_size, dtype=np.float32)

        for i in range(ctx.buffer_size):
            for message in self.midi.buffer.get_messages_at_pos(i):
                if message[0] & Message.OPCODE_MASK == Message.NOTE_ON:
                    self.current_note = message[1]
                elif message[0] & Message.OPCODE_MASK == Message.NOTE_OFF:
                    self.current_note = 0

            output[i] = 440 * (2 ** ((self.current_note - 69) / 12))

        self.frequency.write(output)
