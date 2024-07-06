from pathlib import Path

from lark import Lark

parser = Lark((Path(__file__).parent / 'synchrolang.lark').read_text())
