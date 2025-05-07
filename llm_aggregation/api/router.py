from fastapi import APIRouter

from . import claude
from . import proxy
from ..config import settings

api_router = APIRouter()

# 添加各个 LLM 的路由
api_router.include_router(claude.router, prefix="/api/llm/claude/v1", tags=["Claude"])
api_router.include_router(proxy.router, tags=["proxy"])
