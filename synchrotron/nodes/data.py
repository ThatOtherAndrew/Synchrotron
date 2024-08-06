from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

from . import DataInput, Node, RenderContext, StreamInput, StreamOutput

if TYPE_CHECKING:
    from synchrotron.synchrotron import Synchrotron

__all__ = ['UniformRandomNode', 'AddNode', 'MultiplyNode', 'DebugNode', 'SequenceNode']


class UniformRandomNode(Node):
    min: StreamInput
    max: StreamInput
    out: StreamOutput

    def __init__(self, synchrotron: Synchrotron, name: str) -> None:
        super().__init__(synchrotron, name)
        self.rng = np.random.default_rng()

    def render(self, ctx: RenderContext) -> None:
        low = self.min.read(ctx)[0]
        high = self.max.read(ctx)[0]
        self.out.write(self.rng.uniform(low=low, high=high, size=ctx.buffer_size).astype(np.float32))


class AddNode(Node):
    a: StreamInput
    b: StreamInput
    out: StreamOutput

    def render(self, ctx: RenderContext) -> None:
        self.out.write(self.a.read(ctx) + self.b.read(ctx))


class MultiplyNode(Node):
    a: StreamInput
    b: StreamInput
    out: StreamOutput

    def render(self, ctx: RenderContext) -> None:
        self.out.write(self.a.read(ctx) * self.b.read(ctx))


class DebugNode(Node):
    input: DataInput

    def render(self, _: RenderContext) -> None:
        if self.input.connection is None:
            return
        buffer = self.input.read()
        print(buffer)


class SequenceNode(Node):
    sequence: DataInput
    step: StreamInput
    out: StreamOutput

    def __init__(self, synchrotron: Synchrotron, name: str):
        super().__init__(synchrotron, name)
        self.sequence_position = 0

    def render(self, ctx: RenderContext) -> None:
        step = self.step.read(ctx)
        output = np.empty(shape=ctx.buffer_size, dtype=np.float32)
        sequence = self.sequence.read()

        for i in range(ctx.buffer_size):
            if step[i]:
                self.sequence_position += 1
                self.sequence_position %= len(sequence)
            output[i] = sequence[self.sequence_position]

        self.out.write(output)
