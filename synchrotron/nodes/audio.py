from __future__ import annotations

from queue import Queue
from typing import TYPE_CHECKING

import numpy as np
import pyaudio

from .base import Input, Node, Output, RenderContext

if TYPE_CHECKING:
    from synchrotron import Synchrotron


class SilenceNode(Node):
    out: Output

    def render(self, ctx: RenderContext) -> None:
        self.out.write(np.zeros(shape=ctx.buffer_size, dtype=np.float32))


class SineNode(Node):
    frequency: Input
    out: Output

    def render(self, ctx: RenderContext) -> None:
        frequency = self.frequency.read(ctx)[0]
        sine_window = np.linspace(
            0,
            2 * np.pi * frequency * ctx.buffer_size / ctx.sample_rate,
            num=ctx.buffer_size,
            endpoint=False,
            dtype=np.float32,
        )
        self.out.write(np.sin(sine_window))


class PlaybackNode(Node):
    left: Input
    right: Input

    def __init__(self, synchrotron: Synchrotron, name: str) -> None:
        super().__init__(synchrotron, name)

        self.playback_queue = Queue()
        synchrotron.add_output_queue(self.playback_queue)

        # noinspection PyTypeChecker
        self.stream = synchrotron.pyaudio_session.open(
            rate=synchrotron.sample_rate,
            channels=2,
            format=pyaudio.paFloat32,
            output=True,
            frames_per_buffer=synchrotron.buffer_size,
            stream_callback=self._pyaudio_callback,
        )

    def _pyaudio_callback(self, *_):
        buffer = self.playback_queue.get()
        self.playback_queue.task_done()
        return buffer, pyaudio.paContinue

    def render(self, ctx: RenderContext) -> None:
        left_buffer = self.left.read(ctx)
        right_buffer = self.right.read(ctx)

        stereo_buffer = np.empty(shape=left_buffer.size + right_buffer.size, dtype=np.float32)
        stereo_buffer[0::2] = left_buffer
        stereo_buffer[1::2] = right_buffer
        self.playback_queue.put_nowait(stereo_buffer)
