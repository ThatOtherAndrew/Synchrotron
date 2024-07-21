from fastapi import APIRouter

from . import models
from .dependencies import SynchrotronDependency

router = APIRouter()


@router.get('/start')
async def start_rendering(synchrotron: SynchrotronDependency) -> None:
    synchrotron.start_rendering()


@router.get('/stop')
async def stop_rendering(synchrotron: SynchrotronDependency) -> None:
    synchrotron.stop_rendering()


@router.get('/nodes')
async def get_nodes(synchrotron: SynchrotronDependency) -> list[models.Node]:
    return [models.Node.model_validate(node.as_json()) for node in synchrotron.nodes]


@router.get('/nodes/{node_name}')
async def get_node_by_name(synchrotron: SynchrotronDependency, node_name: str) -> models.Node:
    return models.Node.model_validate(synchrotron.get_node(node_name=node_name).as_json())


# noinspection PyShadowingBuiltins
@router.post('/nodes/{node_name}')
async def create_node(
    synchrotron: SynchrotronDependency,
    node_name: str,
    node_init_data: models.NodeInitData,
) -> models.Node:
    cls = synchrotron.synchrolang_transformer.node_class(class_name=node_init_data.type)
    node = synchrotron.synchrolang_transformer.node_init(
        name=node_name,
        cls=cls,
        args=node_init_data.args,
        kwargs=node_init_data.kwargs,
    )
    return models.Node.model_validate(node.as_json())


@router.delete('/nodes/{node_name}')
async def remove_node(synchrotron: SynchrotronDependency, node_name: str) -> models.Node:
    return models.Node.model_validate(synchrotron.remove_node(node_name).as_json())


@router.get('/connections')
async def get_connections(synchrotron: SynchrotronDependency) -> list[models.Connection]:
    return [models.Connection.model_validate(connection.as_json()) for connection in synchrotron.connections]


@router.patch('/connections')
async def add_connection(synchrotron: SynchrotronDependency, connection: models.Connection) -> models.Connection:
    source = synchrotron.get_node(connection.source.node_name).get_output(connection.source.port_name)
    sink = synchrotron.get_node(connection.sink.node_name).get_input(connection.sink.port_name)
    return models.Connection.model_validate(synchrotron.add_connection(source, sink).as_json())


@router.delete('/connections/')
async def remove_connection(
    synchrotron: SynchrotronDependency,
    connection: models.Connection
) -> models.Connection | None:
    source = synchrotron.get_node(connection.source.node_name).get_output(connection.source.port_name)
    sink = synchrotron.get_node(connection.sink.node_name).get_input(connection.sink.port_name)
    connection = synchrotron.remove_connection(source, sink)

    if connection is None:
        return None
    return models.Connection.model_validate(connection.as_json())
