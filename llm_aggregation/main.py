import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# Change from relative to absolute import
from llm_aggregation.api.router import api_router
from llm_aggregation.config import settings
from llm_aggregation.logger import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动事件
    logger.info("服务启动")
    logger.info(f"服务运行在 http://{settings.server.host}:{settings.server.port}")
    
    yield
    
    # 关闭事件
    logger.info("服务关闭")


app = FastAPI(
    title="LLM 聚合 API",
    description="聚合各大模型 API 的服务，包括 OpenAI、DeepSeek、Claude 等",
    version="0.1.0",
    lifespan=lifespan
)

# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 添加全局异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"全局异常: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": {"message": str(exc), "type": "server_error"}}
    )


# 添加路由
app.include_router(api_router)


# 健康检查
@app.get("/health")
async def health_check():
    logger.debug("健康检查请求")
    return {"status": "ok"}


if __name__ == "__main__":
    logger.info(f"以 {'调试' if settings.server.debug else '生产'} 模式启动服务")
    uvicorn.run(
        "llm_aggregation.main:app",
        host=settings.server.host,
        port=settings.server.port,
        reload=settings.server.debug
    )
