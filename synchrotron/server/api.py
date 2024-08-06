from fastapi import APIRouter
from fastapi.requests import Request

from . import models
from .dependencies import SynchrotronDependency

router = APIRouter()


@router.post('/execute')
async def execute(request: Request, synchrotron: SynchrotronDependency) -> str:
    body = await request.body()
    return_values = synchrotron.execute(body.decode())
    return repr(return_values)


@router.get('/start')
async def start_rendering(synchrotron: SynchrotronDependency) -> None:
    synchrotron.start_rendering()


@router.get('/stop')
async def stop_rendering(synchrotron: SynchrotronDependency) -> None:
    synchrotron.stop_rendering()


@router.get('/export')
async def export_state(synchrotron: SynchrotronDependency) -> str:
    return synchrotron.export_state()


@router.get('/nodes')
async def get_nodes(synchrotron: SynchrotronDependency) -> list[models.Node]:
    return [models.Node.model_validate(node.as_json()) for node in synchrotron.nodes]


# noinspection PyShadowingBuiltins
@router.post('/nodes')
async def create_unnamed_node(
    synchrotron: SynchrotronDependency,
    type: str,
) -> models.Node:
    cls = synchrotron.synchrolang_transformer.node_type(type_name=type)
    node = synchrotron.synchrolang_transformer.create(cls=cls)
    return models.Node.model_validate(node.as_json())


@router.get('/nodes/{node_name}')
async def get_node_by_name(synchrotron: SynchrotronDependency, node_name: str) -> models.Node:
    return models.Node.model_validate(synchrotron.get_node(node_name=node_name).as_json())


# noinspection PyShadowingBuiltins
@router.post('/nodes/{node_name}')
async def create_node(
    synchrotron: SynchrotronDependency,
    node_name: str,
    type: str,
) -> models.Node:
    cls = synchrotron.synchrolang_transformer.node_type(type_name=type)
    node = synchrotron.synchrolang_transformer.create(cls=cls, name=node_name)
    return models.Node.model_validate(node.as_json())


@router.delete('/nodes/{node_name}')
async def remove_node(synchrotron: SynchrotronDependency, node_name: str) -> models.Node:
    return models.Node.model_validate(synchrotron.remove_node(node_name).as_json())


@router.get('/connections')
async def get_connections(synchrotron: SynchrotronDependency) -> list[models.Connection]:
    return [
        models.Connection.model_validate(connection.as_json(connection_assertion=True))
        for connection in synchrotron.connections
    ]


@router.patch('/connections')
async def add_connection(synchrotron: SynchrotronDependency, connection: models.Connection) -> models.Connection:
    source = synchrotron.get_node(connection.source.node_name).get_output(connection.source.port_name)
    sink = synchrotron.get_node(connection.sink.node_name).get_input(connection.sink.port_name)
    return models.Connection.model_validate(synchrotron.add_connection(source, sink).as_json(connection_assertion=True))


@router.delete('/connections')
async def remove_connection(
    synchrotron: SynchrotronDependency,
    connection: models.Connection
) -> models.Connection | None:
    source = synchrotron.get_node(connection.source.node_name).get_output(connection.source.port_name)
    sink = synchrotron.get_node(connection.sink.node_name).get_input(connection.sink.port_name)
    connection = synchrotron.remove_connection(source, sink)

    if connection is None:
        return None
    return models.Connection.model_validate(connection.as_json(connection_assertion=False))
