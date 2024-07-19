from typing import Annotated, TypeAlias

from fastapi import Depends, Request

from synchrotron.synchrotron import Synchrotron


def get_synchrotron_instance(request: Request) -> Synchrotron:
    # noinspection PyUnresolvedReferences
    return request.app.state.synchrotron


SynchrotronDependency: TypeAlias = Annotated[Synchrotron, Depends(get_synchrotron_instance)]
