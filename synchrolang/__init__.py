from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from lark import Lark

if TYPE_CHECKING:
    from typing import TypeAlias


def parser() -> Lark:
    return Lark((Path(__file__).parent / 'synchrolang.lark').read_text())


Value: TypeAlias = str | int | float | list['Value'] | bool | None
