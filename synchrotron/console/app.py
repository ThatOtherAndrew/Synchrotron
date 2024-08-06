from __future__ import annotations

from typing import ClassVar

import aiohttp
from lark.exceptions import VisitError
from rich.highlighter import ReprHighlighter
from rich.markup import escape
from rich.panel import Panel
from textual import events, widgets
from textual.app import App, ComposeResult
from textual.binding import Binding


class OutputLog(widgets.RichLog):
    app: Console

    # noinspection PyShadowingBuiltins
    def __init__(self, id: str) -> None:
        super().__init__(id=id, highlight=True, markup=True)
        self.border_subtitle = 'Synchrotron'


class CommandInput(widgets.TextArea, inherit_bindings=False):
    app: Console

    BINDINGS: ClassVar[list[Binding]] = [
        Binding('enter', action='submit', description='Run command'),
        Binding('ctrl+j', action='newline', description='new line', show=False),

        # The below is an almost-copy of TextArea.BINDINGS but with (imo) more sensible defaults.

        # Cursor movement
        Binding('up', 'cursor_up', 'cursor up', show=False),
        Binding('down', 'cursor_down', 'cursor down', show=False),
        Binding('left', 'cursor_left', 'cursor left', show=False),
        Binding('right', 'cursor_right', 'cursor right', show=False),
        Binding('ctrl+left', 'cursor_word_left', 'cursor word left', show=False),
        Binding('ctrl+right', 'cursor_word_right', 'cursor word right', show=False),
        Binding('home', 'cursor_line_start', 'cursor line start', show=False),
        Binding('end', 'cursor_line_end', 'cursor line end', show=False),
        Binding('pageup', 'cursor_page_up', 'cursor page up', show=False),
        Binding('pagedown', 'cursor_page_down', 'cursor page down', show=False),

        # Making selections (generally holding the shift key and moving cursor)
        Binding('shift+up', 'cursor_up(True)', 'cursor up select', show=False),
        Binding('shift+down', 'cursor_down(True)', 'cursor down select', show=False),
        Binding('shift+left', 'cursor_left(True)', 'cursor left select', show=False),
        Binding('shift+right', 'cursor_right(True)', 'cursor right select', show=False),
        Binding('shift+ctrl+left', 'cursor_word_left(True)', 'cursor left word select', show=False),
        Binding('shift+ctrl+right', 'cursor_word_right(True)', 'cursor right word select', show=False),
        Binding('shift+home', 'cursor_line_start(True)', 'cursor line start select', show=False),
        Binding('shift+end', 'cursor_line_end(True)', 'cursor line end select', show=False),

        # Shortcut ways of making selections
        Binding('ctrl+w', 'select_word', 'select word', show=False),
        Binding('ctrl+l', 'select_line', 'select line', show=False),
        Binding('ctrl+a', 'select_all', 'select all', show=False),

        # Deletion
        # TODO: fix backspace combos not working
        Binding('backspace', 'delete_left', 'delete left', show=False),
        Binding('ctrl+backspace', 'delete_word_left', 'delete left to start of word', show=False),
        Binding('delete', 'delete_right', 'delete right', show=False),
        Binding('ctrl+delete', 'delete_word_right', 'delete right to start of word', show=False),
        Binding('ctrl+y', 'delete_line', 'delete line', show=False),
        Binding('ctrl+shift+backspace', 'delete_to_start_of_line', 'delete to line start', show=False),
        Binding('ctrl+shift+delete', 'delete_to_end_of_line_or_delete_line', 'delete to line end', show=False),

        # Undo and redo
        Binding('ctrl+z', 'undo', 'Undo', show=False),
        Binding('ctrl+shift+z', 'redo', 'Redo', show=False),
    ]

    # noinspection PyShadowingBuiltins
    def __init__(self, id: str) -> None:
        super().__init__(id=id)
        self.border_title = 'Send a command...'
        self.border_subtitle = 'Synchrolang'

    async def on_key(self, event: events.Key) -> None:
        if event.key == 'enter':
            event.stop()
            event.prevent_default()
            await self.action_submit()

    def action_newline(self) -> None:
        start, end = self.selection
        self._replace_via_keyboard('\n', start, end)

    def action_copy(self) -> None:
        # TODO
        ...

    def action_cut(self) -> None:
        # TODO
        ...

    async def action_submit(self) -> None:
        script = self.text
        self.clear()
        self.app.output_log.write('[dim]> ' + escape(script.replace('\n', '\n│ ')))

        try:
            response = await self.app.http_client.post('/execute', data=script)

        except Exception as error:
            if isinstance(error, VisitError):
                error = error.orig_exc
            self.app.output_log.write(Panel(
                ReprHighlighter()(str(error)),
                title=error.__class__.__name__,
                expand=False,
                border_style='red',
            ))
            return

        if response.ok:
            self.app.output_log.write(await response.json())
        else:
            self.app.output_log.write(Panel(
                await response.text(),
                title=f'HTTP {response.status}',
                expand=False,
                border_style='red',
            ))


class Console(App, inherit_bindings=False):
    TITLE = 'Synchrotron'
    SUB_TITLE = 'Console'
    CSS_PATH = 'app.tcss'
    # TODO: fix the below bindings not clickable in the footer
    BINDINGS: ClassVar[list[Binding]] = [
        Binding('ctrl+k', action='command_palette', description='Command palette', priority=True),
        Binding('ctrl+c', action='quit', description='Quit', priority=True),
    ]

    def __init__(self):
        super().__init__()
        self.http_client: aiohttp.ClientSession | None = None
        self.output_log = OutputLog(id='output_log')
        self.command_input = CommandInput(id='command_input')

    def compose(self) -> ComposeResult:
        yield widgets.Header()
        yield self.output_log
        yield self.command_input
        footer = widgets.Footer()
        footer.ctrl_to_caret = False
        yield footer

    async def on_ready(self) -> None:
        self.http_client = aiohttp.ClientSession(base_url='http://localhost:2031')
        self.command_input.focus()

    async def action_quit(self) -> None:
        await self.http_client.close()
        self.exit()


def run_app() -> None:
    Console().run()
