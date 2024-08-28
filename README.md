# Synchrotron

Graph-based live audio manipulation engine implemented in Python

---

## What is it?

Synchrotron is all of the following:
- DSP (Digital Signal Processing) engine
- Audio router / muxer
- Synthesiser
- Audio effects engine
- MIDI instrument
- And more!

It's still very much a baby project, but make no mistake, it can already be pretty powerful! Take a look for yourself:

| [Hack Club Showcase - Synchrotron](https://youtu.be/wlhBz62t2zE)                                                                 |
|----------------------------------------------------------------------------------------------------------------------------------|
| [![Hack Club Showcase - Synchrotron](https://img.youtube.com/vi/wlhBz62t2zE/0.jpg)](https://www.youtube.com/watch?v=wlhBz62t2zE) |

Synchrotron has been designed from the ground up with **maximum flexibility and interoperability in mind**, and as such, there are many ways to use Synchrotron and interact with the server.

This includes (click images to enlarge):

| Blender-inspired node editor UI                                         | Fancy TUI Console                                                       | REST API                                                                | Python API                                                              |
|-------------------------------------------------------------------------|-------------------------------------------------------------------------|-------------------------------------------------------------------------|-------------------------------------------------------------------------|
| [![](https://i.imgur.com/MXSbFcv.png)](https://i.imgur.com/MXSbFcv.png) | [![](https://i.imgur.com/t924jJd.png)](https://i.imgur.com/t924jJd.png) | [![](https://i.imgur.com/AUAx4xs.png)](https://i.imgur.com/AUAx4xs.png) | [![](https://i.imgur.com/j5xTHEa.png)](https://i.imgur.com/j5xTHEa.png) |

The possibilities are endless - whether you wish to render audio to a WAV file on a remote server, or embed the Python package as a dependency for your desktop app. Use Synchrotron as a Python library, interact with its webserver's endpoints through an HTTP client, or use the elegant Synchrolang syntax to control it with just your keyboard.

---

## Installation

Synchrotron can be installed from this repository directly via [pip](https://packaging.python.org/en/latest/tutorials/installing-packages/):

```shell
pip install git+https://github.com/ThatOtherAndrew/Synchrotron
```

Of course, [uv](https://astral.sh/blog/uv) - the faster pip alternative - is also supported:

```shell
uv pip install git+https://github.com/ThatOtherAndrew/Synchrotron
```

## Startup

From the Python environment you installed Synchrotron in, you can start the server:

```shell
synchrotron-server
```

To start the console for a TUI client to interact with the server:

```shell
synchrotron-console
```

## Usage

Synchrotron provides a **Python API**, **[DSL](https://www.jetbrains.com/mps/concepts/domain-specific-languages/)**, and **REST API** for interacting with the *synchrotron server* - the component of Synchrotron which handles the audio rendering and playback.

For the humans, you can find a web-based user interface for Synchrotron at **[ThatOtherAndrew/SynchrotronUI](https://github.com/ThatOtherAndrew/SynchrotronUI)**.

## Random YouTube Video

I recorded myself at a pretty garden in Queens' College in Oxford yapping about dependency graphs: https://youtu.be/qkNqOcH2jWE
