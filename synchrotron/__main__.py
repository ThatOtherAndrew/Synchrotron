import time
from collections.abc import Mapping

import numpy as np
import pyaudio
from numpy.typing import NDArray

import synchrotron.nodes.base
from . import nodes

SAMPLE_RATE = 44100


class Synchrotron(synchrotron.nodes.base.Node):
    def __init__(self):
        super().__init__()
        self.inputs['left'] = synchrotron.nodes.base.Input(self)
        self.inputs['right'] = synchrotron.nodes.base.Input(self)

        self.offset = 0

    def __pyaudio_callback(
        self,
        _: bytes | None,
        frame_count: int,
        __: Mapping[str, float],
        ___: int,
    ) -> tuple[NDArray[np.float32], int]:
        left_buffer = self.inputs['left'].read(self.offset, frame_count)
        right_buffer = self.inputs['right'].read(self.offset, frame_count)
        self.offset += frame_count

        stereo_buffer = np.empty(shape=left_buffer.size + right_buffer.size, dtype=np.float32)
        stereo_buffer[0::2] = left_buffer
        stereo_buffer[1::2] = right_buffer
        return stereo_buffer, pyaudio.paContinue

    def play(self) -> None:
        pyaudio_session = pyaudio.PyAudio()
        # noinspection PyTypeChecker
        stream = pyaudio_session.open(
            rate=SAMPLE_RATE,
            channels=2,
            format=pyaudio.paFloat32,
            output=True,
            frames_per_buffer=SAMPLE_RATE,
            stream_callback=self.__pyaudio_callback,
        )

        try:
            while stream.is_active():
                time.sleep(0.1)
        except KeyboardInterrupt:
            print('Keyboard interrupt received')
        finally:
            print('Closing stream')
            stream.close()
            pyaudio_session.terminate()


if __name__ == '__main__':
    synchrotron = Synchrotron()
    freq_l = nodes.data.ConstantNode(440.)
    sine_l = nodes.audio.SineNode()
    freq_r = nodes.data.ConstantNode(660.)
    sine_r = nodes.audio.SineNode()

    synchrotron.inputs['left'].link(sine_l.outputs['sine'])
    sine_l.inputs['frequency'].link(freq_l.outputs['value'])
    synchrotron.inputs['right'].link(sine_r.outputs['sine'])
    sine_r.inputs['frequency'].link(freq_r.outputs['value'])

    synchrotron.play()
