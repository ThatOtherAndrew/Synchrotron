from typing import Any

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
    type: str
    inputs: list[Input]
    outputs: list[Output]
    exports: dict[str, Any]


class Connection(BaseModel):
    source: Port
    sink: Port
