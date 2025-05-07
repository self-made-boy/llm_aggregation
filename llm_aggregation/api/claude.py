import json
import traceback

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from starlette.responses import JSONResponse

from ..services.claude_service import ClaudeService
from ..logger import logger

router = APIRouter()
service = ClaudeService()


@router.post("/messages")
async def messages(request: Request):
    """
    Claude 聊天补全 API
    """
    try:
        # 直接从请求中获取 JSON 数据
        request_data = await request.body()
        api_key = request.headers.get("x-api-key")
        if api_key is None:
            api_key = request.headers.get('authorization')
            if api_key is not None and api_key.startswith("Bearer "):
                api_key = api_key[len("Bearer "):]



        if not service.check_key(api_key):
            raise HTTPException(status_code=403, detail="Invalid API key")

        for item in request.headers.items():
            logger.info(f"{item[0]}: {item[1]}")

        json_str = request_data.decode('utf-8')
        logger.info(json_str)

        request_json = json.loads(json_str)
        is_stream = request_json.get("stream", True)
        if is_stream:
            return StreamingResponse(service.streaming_messages(request_json))
        else:

            return JSONResponse(content=await service.messages(request_json))



    except Exception as e:
        print(e)
        traceback.print_exc()
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail={"message": str(e), "type": "server_error"})


@router.get("/models")
async def model(request: Request):
    """
    获取模型列表
    """
    return service.get_models()
