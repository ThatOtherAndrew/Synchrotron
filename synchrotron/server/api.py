from fastapi import APIRouter

from . import models
from .dependencies import SynchrotronDependency

router = APIRouter()


@router.get('/nodes')
async def get_nodes(synchrotron: SynchrotronDependency) -> list[models.Node]:
    return [models.Node(node) for node in synchrotron.nodes]
