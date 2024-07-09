from __future__ import annotations

from typing import ClassVar

from lark.exceptions import VisitError
from rich.highlighter import ReprHighlighter
from rich.markup import escape
from rich.panel import Panel
from textual import widgets
from textual.app import App, ComposeResult
from textual.binding import Binding

from synchrotron import Synchrotron


class OutputLog(widgets.RichLog):
    app: Console

    # noinspection PyShadowingBuiltins
    def __init__(self, id: str) -> None:
        super().__init__(id=id, highlight=True, markup=True)
        self.border_subtitle = 'Synchrotron'


class CommandInput(widgets.TextArea):
    app: Console

    BINDINGS: ClassVar[list[Binding]] = [
        Binding('ctrl+s', action='submit', description='Run command')
    ]

    # noinspection PyShadowingBuiltins
    def __init__(self, id: str) -> None:
        super().__init__(id=id)
        self.border_title = 'Send a command...'
        self.border_subtitle = 'Synchrolang'

    def action_submit(self) -> None:
        expression = self.text
        self.clear()
        self.app.output_log.write('[dim]> ' + escape(expression))

        try:
            return_data = self.app.synchrotron.execute(expression)
        except Exception as error:
            if isinstance(error, VisitError):
                error = error.orig_exc
            return_data = Panel(
                ReprHighlighter()(str(error)),
                title=error.__class__.__name__,
                expand=False,
                border_style='red',
            )

        self.app.output_log.write(return_data)


class Console(App, inherit_bindings=False):
    TITLE = 'Synchrotron'
    SUB_TITLE = 'Console'
    CSS_PATH = 'app.tcss'
    BINDINGS: ClassVar[list[Binding]] = [
        Binding('ctrl+k', action='command_palette', description='Command Palette', priority=True),
        Binding('ctrl+c', action='quit', description='Quit', priority=True),
    ]

    def __init__(self):
        super().__init__()
        self.synchrotron = Synchrotron(buffer_size=22050)
        self.output_log = OutputLog(id='output_log')
        self.command_input = CommandInput(id='command_input')

    def compose(self) -> ComposeResult:
        yield widgets.Header()
        yield self.output_log
        yield self.command_input
        footer = widgets.Footer()
        footer.ctrl_to_caret = False
        yield footer

    def on_ready(self) -> None:
        self.command_input.focus()

        self.output_log.write('[bold cyan]Starting Synchrotron server')
        self.synchrotron.start_server()

    def action_quit(self) -> None:
        self.synchrotron.stop_server()
        self.exit()
