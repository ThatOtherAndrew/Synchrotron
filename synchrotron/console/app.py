from __future__ import annotations

from typing import TYPE_CHECKING

from lark.exceptions import VisitError
from rich.highlighter import ReprHighlighter
from rich.markup import escape
from rich.panel import Panel
from textual import widgets
from textual.app import App, ComposeResult

if TYPE_CHECKING:
    from ..__main__ import Synchrotron


class OutputLog(widgets.RichLog):
    app: Console

    # noinspection PyShadowingBuiltins
    def __init__(self, id: str) -> None:
        super().__init__(id=id, highlight=True, markup=True)
        self.border_subtitle = 'Synchrotron'


class CommandInput(widgets.Input):
    app: Console

    # noinspection PyShadowingBuiltins
    def __init__(self, id: str) -> None:
        super().__init__(id=id, placeholder='Send a command...')
        self.border_subtitle = 'Synchrolang'

    def action_submit(self) -> None:
        expression = self.value
        self.app.output_log.write('[dim]> [cyan]' + escape(expression))

        try:
            return_data = self.app.synchrotron.execute(expression)
        except Exception as error:
            if isinstance(error, VisitError):
                error = error.orig_exc
            return_data = Panel(
                ReprHighlighter()(str(error)),
                title=error.__class__.__name__,
                expand=False,
                border_style='red'
            )

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
