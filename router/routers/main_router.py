from typing import List

from fastapi import APIRouter

from router import api_logger
from router.routers.routes import router_router
from router.routers.routes import user_router

TAG_ROOT = "root"

router = APIRouter()
logger = api_logger.get()

routers_to_include: List[APIRouter] = [
    router_router.router,
    user_router.router,
]
for router_to_include in routers_to_include:
    router.include_router(router_to_include)
