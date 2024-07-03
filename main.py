import time
from collections.abc import Mapping

import pyaudio

import node

SAMPLE_RATE = 44100


class Synchrotron(node.Node):
    def __init__(self):
        super().__init__()
        self.inputs['master'] = node.Input(self)

        self.offset = 0

    def __pyaudio_callback(
        self,
        _: bytes | None,
        frame_count: int,
        __: Mapping[str, float],
        ___: int,
    ) -> tuple[bytes | None, int]:
        buffer = self.inputs['master'].read(self.offset, frame_count)
        self.offset += frame_count
        return buffer, pyaudio.paContinue

    def play(self) -> None:
        pyaudio_session = pyaudio.PyAudio()
        stream = pyaudio_session.open(
            rate=SAMPLE_RATE,
            channels=1,
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
    freq = node.ConstantNode(440.)
    sine = node.SineNode()
    debugger = node.DebugNode()

    synchrotron.inputs['master'].link(debugger.outputs['out'])
    debugger.inputs['in'].link(sine.outputs['sine'])
    sine.inputs['frequency'].link(freq.outputs['value'])

    synchrotron.play()
