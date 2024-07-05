from __future__ import annotations

from typing import Any

import numpy as np

from .base import Input, Node, Output, RenderContext


class ConstantNode(Node):
    out: Output

    def __init__(self, value: Any) -> None:
        super().__init__()
        self.value = value

    def render(self, ctx: RenderContext) -> None:
        self.out.write(np.full(shape=ctx.buffer_size, fill_value=self.value, dtype=np.float32))


class UniformRandomNode(Node):
    min: Input
    max: Input
    out: Output

    def __init__(self) -> None:
        super().__init__()
        self.rng = np.random.default_rng()

    def render(self, ctx: RenderContext) -> None:
        low = self.min.read()[0]
        high = self.max.read()[0]
        self.out.write(self.rng.uniform(low=low, high=high, size=ctx.buffer_size).astype(np.float32))


class DebugNode(Node):
    input: Input

    def render(self, _: RenderContext) -> None:
        buffer = self.input.read()
        print(buffer)