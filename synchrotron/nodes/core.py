from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

from . import Input, Node, Output, RenderContext

if TYPE_CHECKING:
    from synchrotron.synchrotron import Synchrotron

__all__ = ['DataNode', 'StreamNode']


class DataNode(Node):
    out: Output

    def __init__(self, synchrotron: Synchrotron, name: str, value: float) -> None:
        super().__init__(synchrotron, name)
        self.value = value
        self.exports['Value'] = value

    def render(self, ctx: RenderContext) -> None:
        self.out.write(np.full(shape=ctx.buffer_size, fill_value=self.value, dtype=np.float32))


class StreamNode(Node):
    data: Input
    out: Output

    def render(self, ctx: RenderContext) -> None:
        self.out.write(np.full(shape=ctx.buffer_size, fill_value=self.data.read(ctx), dtype=np.float32))
