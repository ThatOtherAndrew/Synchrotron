import time
from collections.abc import Mapping

import numpy as np
import pyaudio

SAMPLE_RATE = 44100


def audio_callback(
    in_data: bytes | None,
    frame_count: int,
    time_info: Mapping[str, float],
    status: int,
) -> tuple[bytes | None, int]:

    sine = np.sin(np.arange(0, 440 * frame_count, 440, dtype=np.float32))
    return sine, pyaudio.paContinue


if __name__ == '__main__':
    session = pyaudio.PyAudio()
    stream = session.open(
        rate=SAMPLE_RATE,
        channels=1,
        format=pyaudio.paFloat32,
        output=True,
        frames_per_buffer=440,
        stream_callback=audio_callback,
    )
    while stream.is_active():
        time.sleep(0.1)
    stream.close()
    session.terminate()
