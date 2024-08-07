from __future__ import annotations

from typing import TYPE_CHECKING

import mido
import numpy as np

from . import MidiInput, Node, RenderContext, StreamOutput

if TYPE_CHECKING:
    from synchrotron.synchrotron import Synchrotron


class MonophonicRenderNode(Node):
    midi: MidiInput
    frequency: StreamOutput

    def __init__(self, synchrotron: Synchrotron, name: str):
        super().__init__(synchrotron, name)
        self.current_note: mido.Message | None = None
        self.current_frequency = 0

    def render(self, ctx: RenderContext) -> None:
        output = np.empty(shape=ctx.buffer_size, dtype=np.float32)

        for message in self.midi.read():
            if not message.is_meta:
                if message.type == 'note_off':
                    ...  # TODO: actually finish this off

        self.frequency.write(output)
