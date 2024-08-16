from __future__ import annotations

from pathlib import Path
from queue import Queue
from typing import TYPE_CHECKING

import numpy as np
import pyaudio
from soundfile import SoundFile

from . import DataInput, Node, RenderContext, StreamInput, StreamOutput

if TYPE_CHECKING:
    from synchrotron.synchrotron import Synchrotron

__all__ = ['SilenceNode', 'SineNode', 'SquareNode', 'SawtoothNode', 'PlaybackNode', 'WavFileNode']


class SilenceNode(Node):
    out: StreamOutput

    def render(self, ctx: RenderContext) -> None:
        self.out.write(np.zeros(shape=ctx.buffer_size, dtype=np.float32))


class SineNode(Node):
    frequency: StreamInput
    out: StreamOutput

    def __init__(self, synchrotron: Synchrotron, name: str) -> None:
        super().__init__(synchrotron, name)
        self.phase = 0.

    def render(self, ctx: RenderContext) -> None:
        frequency = self.frequency.read(ctx)
        waveform = np.empty(shape=ctx.buffer_size, dtype=np.float32)

        for i in range(ctx.buffer_size):
            waveform[i] = self.phase
            self.phase += 2 * np.pi * frequency[i] / ctx.sample_rate
            self.phase %= 2 * np.pi

        self.out.write(np.sin(waveform))


class SquareNode(Node):
    frequency: StreamInput
    pwm: StreamInput
    out: StreamOutput

    def __init__(self, synchrotron: Synchrotron, name: str) -> None:
        super().__init__(synchrotron, name)
        self.phase = 0.

    def render(self, ctx: RenderContext) -> None:
        frequency = self.frequency.read(ctx)
        waveform = np.empty(shape=ctx.buffer_size, dtype=np.float32)
        pwm_threshold = self.pwm.read(ctx, default_constant=0.5)

        for i in range(ctx.buffer_size):
            waveform[i] = 1 if self.phase > pwm_threshold[i] else -1
            self.phase += frequency[i] / ctx.sample_rate
            self.phase %= 1

        self.out.write(waveform)


class SawtoothNode(Node):
    frequency: StreamInput
    out: StreamOutput

    def __init__(self, synchrotron: Synchrotron, name: str) -> None:
        super().__init__(synchrotron, name)
        self.phase = 0.

    def render(self, ctx: RenderContext) -> None:
        frequency = self.frequency.read(ctx)
        waveform = np.empty(shape=ctx.buffer_size, dtype=np.float32)

        for i in range(ctx.buffer_size):
            waveform[i] = self.phase
            self.phase += frequency[i] / ctx.sample_rate
            self.phase %= 1

        self.out.write(waveform)


class PlaybackNode(Node):
    left: StreamInput
    right: StreamInput

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

        self.exports['Device'] = synchrotron.pyaudio_session.get_default_output_device_info().get('name')

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


class WavFileNode(Node):
    path: DataInput
    signal: StreamInput

    def __init__(self, synchrotron: Synchrotron, name: str):
        super().__init__(synchrotron, name)

        path = Path(self.path.read(default='output.wav')).resolve()
        self.file = SoundFile(path, mode='wb', samplerate=synchrotron.sample_rate, channels=1, subtype='FLOAT')

        self.exports['File Path'] = path.as_posix()

    def render(self, ctx: RenderContext) -> None:
        self.file.write(self.signal.read(ctx))

    def teardown(self) -> None:
        self.file.close()
