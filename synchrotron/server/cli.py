from typer import Typer

cli = Typer()


@cli.command()
def main(host: str = 'localhost', port: int = 2031):
    import contextlib

    import uvicorn

    from . import server

    with contextlib.suppress(KeyboardInterrupt):
        uvicorn.run(server.app, host=host, port=port)
