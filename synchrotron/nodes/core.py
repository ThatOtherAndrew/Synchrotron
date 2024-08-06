from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

from . import DataInput, DataOutput, Node, RenderContext, StreamOutput

if TYPE_CHECKING:
    from synchrotron.synchrotron import Synchrotron

__all__ = ['DataNode', 'StreamNode']


class DataNode(Node):
    out: DataOutput

    def __init__(self, synchrotron: Synchrotron, name: str, value: float) -> None:
        super().__init__(synchrotron, name)
        self.value = value
        self.exports['Value'] = value

    def render(self, _: RenderContext) -> None:
        self.out.write(self.value)


class StreamNode(Node):
    data: DataInput
    out: StreamOutput

    def render(self, ctx: RenderContext) -> None:
        self.out.write(np.full(shape=ctx.buffer_size, fill_value=self.data.read(), dtype=np.float32))
