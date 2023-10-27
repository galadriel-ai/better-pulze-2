from starlette.routing import Match
from starlette.requests import Request
from typing import Tuple


def get_path_template(request: Request) -> Tuple[str, bool]:
    for route in request.app.routes:
        match, child_scope = route.matches(request.scope)
        if match == Match.FULL:
            return route.path, True

    return request.url.path, False
