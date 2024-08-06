from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

from . import DataInput, Node, RenderContext, StreamInput, StreamOutput

if TYPE_CHECKING:
    from synchrotron.synchrotron import Synchrotron

__all__ = ['UniformRandomNode', 'AddNode', 'MultiplyNode', 'DebugNode']


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
