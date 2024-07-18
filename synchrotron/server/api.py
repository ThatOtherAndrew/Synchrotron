from fastapi import APIRouter

from . import models
from .dependencies import SynchrotronDependency

router = APIRouter()


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
