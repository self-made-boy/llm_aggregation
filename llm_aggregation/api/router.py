from fastapi import APIRouter

from . import openai, deepseek, claude

api_router = APIRouter()

# 添加各个 LLM 的路由
api_router.include_router(openai.router, prefix="/api/llm/openai/v1", tags=["OpenAI"])
api_router.include_router(deepseek.router, prefix="/api/llm/openai/deepseek/v1", tags=["DeepSeek"])
api_router.include_router(claude.router, prefix="/api/llm/claude/v1", tags=["Claude"])
