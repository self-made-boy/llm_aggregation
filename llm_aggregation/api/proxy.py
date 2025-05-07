import httpx
from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from fastapi.responses import PlainTextResponse

from ..config import settings

router = APIRouter()


@router.api_route("{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"])
async def messages(request: Request, path: str):
    target = ""
    for k, v in settings.proxy_path_mapping.items():
        if path.startswith(k):
            target = v + path.removeprefix(k)
            break
    if target == "":
        return PlainTextResponse(status_code=404, content="Not Found")

    # 获取请求头
    headers = dict(request.headers)
    # 可能需要去掉一些特定的头部
    headers.pop("host", None)
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
