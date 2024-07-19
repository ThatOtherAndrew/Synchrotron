from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

from .base import Input, Node, Output, RenderContext

if TYPE_CHECKING:
    from synchrotron.synchrotron import Synchrotron


class ConstantNode(Node):
    out: Output

    def __init__(self, synchrotron: Synchrotron, name: str, value: float) -> None:
        super().__init__(synchrotron, name)
        self.value = value

    def render(self, ctx: RenderContext) -> None:
        self.out.write(np.full(shape=ctx.buffer_size, fill_value=self.value, dtype=np.float32))


class UniformRandomNode(Node):
    min: Input
    max: Input
    out: Output

    def __init__(self, synchrotron: Synchrotron, name: str) -> None:
        super().__init__(synchrotron, name)
        self.rng = np.random.default_rng()

    def render(self, ctx: RenderContext) -> None:
        low = self.min.read(ctx)[0]
        high = self.max.read(ctx)[0]
        self.out.write(self.rng.uniform(low=low, high=high, size=ctx.buffer_size).astype(np.float32))


class AddNode(Node):
    a: Input
    b: Input
    out: Output

    def render(self, ctx: RenderContext) -> None:
        self.out.write(self.a.read(ctx) + self.b.read(ctx))


class MultiplyNode(Node):
    a: Input
    b: Input
    out: Output

    def render(self, ctx: RenderContext) -> None:
        self.out.write(self.a.read(ctx) * self.b.read(ctx))


class DebugNode(Node):
    input: Input

    def render(self, ctx: RenderContext) -> None:
        if self.input.connection is None:
            return
        buffer = self.input.read(ctx)
        print(buffer)
