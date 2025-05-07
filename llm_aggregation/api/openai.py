import httpx
from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from fastapi.responses import PlainTextResponse

from ..config import settings

router = APIRouter()

child_key = settings.openai.child_keys.split(',') if settings.openai.child_keys else []


@router.api_route("{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"])
async def messages(request: Request, path: str):
    target = settings.openai.api_base + path

    # 获取请求头
    headers = dict(request.headers)
    # 可能需要去掉一些特定的头部
    headers.pop("host", None)
    auth_key = headers.get("authorization", None)
    if auth_key is not None:
        if auth_key.startswith("Bearer "):
            auth_key = auth_key.removeprefix("Bearer ")
        if auth_key in child_key:
            headers["authorization"] = f"Bearer {settings.openai.api_key}"


    query_params = dict(request.query_params)
    body = await request.body()
    async with httpx.AsyncClient() as client:
        try:
            response = await client.request(
                method=request.method,
                url=target,
                headers=headers,
                params=query_params,
                content=body,
                timeout=30.0
            )
            return StreamingResponse(
                content=response.aiter_bytes(),
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.headers.get("content-type", "")
            )
        except Exception as e:
            return PlainTextResponse(status_code=500, content=str(e))
