from __future__ import annotations

from typing import Literal

from pydantic import BaseModel


class Port(BaseModel):
    node_name: str
    port_name: str


class BaseInput(Port):
    port_type: Literal['input']


class Input(BaseInput):
    connection: Connection | None


class BaseOutput(Port):
    port_type: Literal['output']


class Output(BaseOutput):
    connections: list[Connection]


class Connection(BaseModel):
    source: BaseOutput
    sink: BaseInput
    is_connected: bool


class Node(BaseModel):
    name: str
    class_name: str
    inputs: list[Input]
    outputs: list[Output]
