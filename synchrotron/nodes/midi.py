from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

from . import Message, MidiInput, Node, RenderContext, StreamOutput

if TYPE_CHECKING:
    from synchrotron.synchrotron import Synchrotron


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
                    # TODO: finish this off

        self.frequency.write(output)
