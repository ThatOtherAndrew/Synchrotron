import time
from collections.abc import Mapping

import numpy as np
import pyaudio

SAMPLE_RATE = 44100


class Synchrotron:
    def __init__(self):
        self.sample_clock = 0

    def get_buffer(self, length: int):
        sine_window = np.linspace(
            0,
            2 * np.pi * 440 * SAMPLE_RATE / length,
            num=length,
            endpoint=False,
            dtype=np.float32
        )
        return np.sin(sine_window)

    def __pyaudio_callback(
        self,
        in_data: bytes | None,
        frame_count: int,
        time_info: Mapping[str, float],
        status: int,
    ) -> tuple[bytes | None, int]:
        buffer = self.get_buffer(length=frame_count)
        self.sample_clock += frame_count
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
    synchrotron.play()
