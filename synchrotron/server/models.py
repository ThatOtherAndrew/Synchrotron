from __future__ import annotations

from pydantic import BaseModel


class Port(BaseModel):
    node_name: str
    port_name: str


class Input(Port):
    source: Port | None


class Output(Port):
    sinks: list[Port]


class Node(BaseModel):
    name: str
    class_name: str
    inputs: list[Input]
    outputs: list[Output]
