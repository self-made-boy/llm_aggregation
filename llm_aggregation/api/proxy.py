import httpx
from fastapi import APIRouter, Request
from fastapi.responses import PlainTextResponse

from ..config import settings
from .streaming_response import ProxyStreamingResponse

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
    
    async def stream_proxy():
        async with httpx.AsyncClient() as client:
            try:
                async with client.stream(
                    method=request.method,
                    url=target,
                    headers=headers,
                    params=query_params,
                    content=body,
                    timeout=30.0
                ) as response:
                    # 首先发送状态码和头信息
                    yield (response.status_code, dict(response.headers), b"")
                    
                    # 然后流式传输数据
                    async for chunk in response.aiter_bytes():
                        yield chunk
            except Exception as e:
                yield (500, {"content-type": "text/plain"}, str(e).encode())
    
    try:
        return ProxyStreamingResponse(content=stream_proxy())
    except Exception as e:
        return PlainTextResponse(status_code=500, content=str(e))
