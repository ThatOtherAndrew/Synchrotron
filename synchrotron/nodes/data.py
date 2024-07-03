from __future__ import annotations

from typing import Any

from .base import Input, Node, Output


class ConstantNode(Node):
    def __init__(self, value: Any) -> None:
        super().__init__()
        self.outputs['value'] = Output(self, self.value)

        self.value = value

    def value(self, _: int, __: int) -> Any:
        return self.value


class DebugNode(Node):
    def __init__(self) -> None:
        super().__init__()
        self.inputs['in'] = Input(self)
        self.outputs['out'] = Output(self, self.out)

    def out(self, offset: int, duration: int) -> Any:
        buffer = self.inputs['in'].read(offset, duration)
        print(buffer)
        return buffer
