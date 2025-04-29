from fastapi import APIRouter, HTTPException, Request
from typing import Dict, Any

from ..services.openai_service import OpenAIService
from ..models.request_models import ChatCompletionRequest, ChatCompletionResponse, ErrorResponse

router = APIRouter()
service = OpenAIService()


@router.post("/chat/completions", response_model=ChatCompletionResponse, responses={400: {"model": ErrorResponse}})
async def chat_completions(request: ChatCompletionRequest):
    """
    OpenAI 聊天补全 API
    """
    try:
        response = await service.chat_completion(request.dict())
        
        if "error" in response:
            raise HTTPException(status_code=400, detail=response["error"])
        
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail={"message": str(e), "type": "server_error"})


@router.post("/{path:path}")
async def proxy_request(path: str, request: Request):
    """
    代理其他 OpenAI API 请求
    """
    # 这里可以实现对其他 OpenAI API 的代理
    raise HTTPException(status_code=501, detail={"message": "API 尚未实现", "type": "not_implemented"})