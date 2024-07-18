from __future__ import annotations

from typing import Literal

from pydantic import BaseModel


class Port(BaseModel):
    node_name: str
    port_name: str


class BaseInput(Port):
    port_type: Literal['input']


class Input(BaseInput):
    source: BaseOutput | None


class BaseOutput(Port):
    port_type: Literal['output']


class Output(BaseOutput):
    sinks: list[BaseInput]


class Node(BaseModel):
    name: str
    class_name: str
    inputs: list[Input]
    outputs: list[Output]
