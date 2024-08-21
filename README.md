# Synchrotron

Graph-based live audio manipulation engine implemented in Python

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
