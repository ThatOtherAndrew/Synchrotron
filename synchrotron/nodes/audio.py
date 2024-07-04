from __future__ import annotations

from typing import TYPE_CHECKING, Any

import numpy as np
import pyaudio

from .base import Input, Node, Output

if TYPE_CHECKING:
    from collections.abc import Mapping

    from numpy.typing import NDArray

    from ..__main__ import Synchrotron


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


class PlaybackNode(Node):
    def __init__(self, synchrotron: Synchrotron) -> None:
        super().__init__()
        self.inputs['left'] = Input(self)
        self.inputs['right'] = Input(self)

        self.synchrotron = synchrotron
        # noinspection PyTypeChecker
        self.stream = synchrotron.pyaudio_session.open(
            rate=synchrotron.sample_rate,
            channels=2,
            format=pyaudio.paFloat32,
            output=True,
            frames_per_buffer=synchrotron.sample_rate,
            stream_callback=self.__pyaudio_callback,
        )

    def __pyaudio_callback(
        self,
        _: bytes | None,
        frame_count: int,
        __: Mapping[str, float],
        ___: int,
    ) -> tuple[NDArray[np.float32], int]:
        left_buffer = self.inputs['left'].read(self.synchrotron.global_clock, frame_count)
        right_buffer = self.inputs['right'].read(self.synchrotron.global_clock, frame_count)
        self.synchrotron.global_clock += frame_count

        stereo_buffer = np.empty(shape=left_buffer.size + right_buffer.size, dtype=np.float32)
        stereo_buffer[0::2] = left_buffer
        stereo_buffer[1::2] = right_buffer
        return stereo_buffer, pyaudio.paContinue

    def start_streaming(self) -> None:
        self.stream.start_stream()
