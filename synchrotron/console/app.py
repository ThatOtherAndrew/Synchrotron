from __future__ import annotations

from typing import TYPE_CHECKING

from rich.markup import escape
from textual import widgets
from textual.app import App, ComposeResult

from . import synchrolang

if TYPE_CHECKING:
    from ..__main__ import Synchrotron


class OutputLog(widgets.RichLog):
    app: Console

    # noinspection PyShadowingBuiltins
    def __init__(self, id: str) -> None:
        super().__init__(id=id, highlight=True, markup=True)


class CommandInput(widgets.Input):
    app: Console

    # noinspection PyShadowingBuiltins
    def __init__(self, id: str) -> None:
        super().__init__(id=id, placeholder='Send a command...')

    def action_submit(self) -> None:
        command = self.value
        self.app.output_log.write('[bright_black]' + escape(f'> {command}'))

        try:
            return_data = synchrolang.parser.parse(command)
        except Exception as error:
            return_data = str(error)

        self.app.output_log.write(return_data)


class Console(App):
    TITLE = 'Synchrotron'
    SUB_TITLE = 'Console'
    CSS_PATH = 'app.tcss'

    def __init__(self, synchrotron: Synchrotron):
        super().__init__()
        self.synchrotron = synchrotron
        self.output_log = OutputLog(id='output_log')
        self.command_input = CommandInput(id='command_input')

    def compose(self) -> ComposeResult:
        yield widgets.Header()
        yield self.output_log
        yield self.command_input
        yield widgets.Footer()

    def on_ready(self) -> None:
        self.output_log.write('[bold green]Synchrotron console successfully started')
        self.command_input.focus()
