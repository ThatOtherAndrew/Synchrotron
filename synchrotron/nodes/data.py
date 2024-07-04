from __future__ import annotations

from typing import Any

import numpy as np

from .base import Input, Node, Output, RenderContext


class ConstantNode(Node):
    def __init__(self, value: Any) -> None:
        super().__init__()
        self.outputs['value'] = Output(self)
        self.value = value

    def render(self, ctx: RenderContext) -> None:
        self.outputs['value'].write(np.full(shape=ctx.buffer_size, fill_value=self.value, dtype=np.float32))


class DebugNode(Node):
    def __init__(self) -> None:
        super().__init__()
        self.inputs['in'] = Input(self)
        self.outputs['out'] = Output(self)

    def render(self, _: RenderContext) -> None:
        buffer = self.inputs['in'].read()
        print(buffer)
        self.outputs['out'].write(buffer)
