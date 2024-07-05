from __future__ import annotations

from typing import TYPE_CHECKING

from textual import widgets
from textual.app import App, ComposeResult

if TYPE_CHECKING:
    from ..__main__ import Synchrotron


class CommandInput(widgets.Input):
    # noinspection PyUnresolvedReferences
    def action_submit(self) -> None:
        command = self.value
        try:
            return_value = eval(command)  # noqa: S307
        except Exception as error:
            return_value = str(error)
        self.app.output_log.write(f'> {command}')
        self.app.output_log.write(return_value)


class Console(App):
    TITLE = 'Synchrotron'
    SUB_TITLE = 'Console'
    CSS_PATH = 'app.tcss'

    def __init__(self, synchrotron: Synchrotron):
        super().__init__()
        self.synchrotron = synchrotron
        self.output_log = widgets.RichLog(id='output_log')
        self.command_input = CommandInput(id='command_input')

    def compose(self) -> ComposeResult:
        yield widgets.Header()
        yield self.output_log
        yield self.command_input
        yield widgets.Footer()
