from __future__ import annotations

from typing import Any

import numpy as np

from .base import Input, Node, Output


class SilenceNode(Node):
    def __init__(self) -> None:
        super().__init__()
        self.outputs['silence'] = Output(self, self.silence)

    @staticmethod
    def silence(_: int, duration: int) -> Any:
        return np.zeros(shape=duration, dtype=np.float32)


class SineNode(Node):
    def __init__(self) -> None:
        super().__init__()
        self.inputs['frequency'] = Input(self)
        self.outputs['sine'] = Output(self, self.sine)

    def sine(self, offset: int, duration: int):
        frequency = self.inputs['frequency'].read(offset, duration)
        sine_window = np.linspace(
            0,
            2 * np.pi * frequency * 44100 / duration,
            num=duration,
            endpoint=False,
            dtype=np.float32
        )
        return np.sin(sine_window)
