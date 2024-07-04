import time

import pyaudio

from . import nodes


class Synchrotron:
    def __init__(self, sample_rate: int = 44100):
        self.pyaudio_session = pyaudio.PyAudio()
        self.global_clock = 0

        # It'd be cool to have a dynamic sample rate, but it would be such an implementation headache
        self.sample_rate = sample_rate

    def play(self, playback_node: nodes.audio.PlaybackNode) -> None:
        playback_node.start_streaming()
        try:
            while playback_node.stream.is_active():
                time.sleep(0.1)
        except KeyboardInterrupt:
            print('Keyboard interrupt received')
        finally:
            print('Closing stream')
            playback_node.stream.close()
            self.pyaudio_session.terminate()


if __name__ == '__main__':
    synchrotron = Synchrotron()
    output = nodes.audio.PlaybackNode(synchrotron)
    freq_l = nodes.data.ConstantNode(440.)
    sine_l = nodes.audio.SineNode()
    freq_r = nodes.data.ConstantNode(660.)
    sine_r = nodes.audio.SineNode()

    output.inputs['left'].link(sine_l.outputs['sine'])
    sine_l.inputs['frequency'].link(freq_l.outputs['value'])
    output.inputs['right'].link(sine_r.outputs['sine'])
    sine_r.inputs['frequency'].link(freq_r.outputs['value'])

    synchrotron.play(output)
