from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
from rtmidi import MidiIn

from . import DataInput, MidiBuffer, MidiInput, MidiMessage, MidiOutput, Node, RenderContext, StreamOutput

if TYPE_CHECKING:
    from synchrotron.synchrotron import Synchrotron

__all__ = ['MidiInputNode', 'MonophonicRenderNode']


class MidiInputNode(Node):
    port: DataInput
    out: MidiOutput

    def __init__(self, synchrotron: Synchrotron, name: str):
        super().__init__(synchrotron, name)

        self.current_port = self.port.read(default=0)
        self.midi_in = MidiIn().open_port(self.current_port)
        self.last_message_time = 0.

        self.exports['Available Ports'] = self.midi_in.get_ports()
        self.exports['Selected Port'] = self.midi_in.get_port_name(self.current_port)

    def render(self, ctx: RenderContext) -> None:
        if (new_port := self.port.read()) != self.current_port:
            self.midi_in.close_port()
            self.midi_in.open_port(new_port)
            self.current_port = new_port
            self.last_message_time = 0.
            self.exports['Available Ports'] = self.midi_in.get_ports()
            self.exports['Selected Port'] = self.midi_in.get_port_name(new_port)

        buffer = MidiBuffer(length=ctx.buffer_size)

        while message := self.midi_in.get_message():
            # https://spotlightkid.github.io/python-rtmidi/rtmidi.html#rtmidi.MidiIn.get_message
            message: tuple[list[int], float]

            self.last_message_time += message[1]
            sample_offset = int((self.last_message_time * ctx.sample_rate) % ctx.buffer_size)

            buffer.add_message(position=sample_offset, message=bytes(message[0]))

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
                if message[0] & MidiMessage.OPCODE_MASK == MidiMessage.NOTE_ON:
                    self.current_note = message[1]
                elif message[0] & MidiMessage.OPCODE_MASK == MidiMessage.NOTE_OFF:
                    if message[1] != self.current_note:
                        continue
                    self.current_note = 0

            output[i] = 440 * (2 ** ((self.current_note - 69) / 12))

        self.frequency.write(output)
