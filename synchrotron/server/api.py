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
