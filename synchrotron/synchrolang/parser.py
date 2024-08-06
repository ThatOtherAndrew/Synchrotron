from pathlib import Path

from lark import Lark


class SynchrolangParser(Lark):
    def __init__(self):
        super().__init__(
            grammar=(Path(__file__).parent / 'synchrolang.lark').read_text(),
            parser='lalr',
            lexer='contextual',
        )
