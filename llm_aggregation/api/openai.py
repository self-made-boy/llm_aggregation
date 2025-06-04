import asyncio
import httpx
from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from fastapi.responses import PlainTextResponse
from typing import AsyncGenerator, Any

from ..config import settings

router = APIRouter()

child_key = settings.openai.child_keys.split(',') if settings.openai.child_keys else []


class ProxyStreamingResponse(StreamingResponse):
    def __init__(self, content: AsyncGenerator[Any, None]):
        super().__init__(content=content)
        self._response_started = False
    
    async def stream_response(self, send):
        async for chunk in self.body_iterator:
            if isinstance(chunk, tuple):  # (status_code, headers, data)
                if not self._response_started:
                    status_code, headers, data = chunk
                    self.status_code = status_code
                    self.headers.update(headers)
                    self.media_type = headers.get("content-type", "")
                    
                    await send({
                        "type": "http.response.start",
                        "status": self.status_code,
                        "headers": self.raw_headers,
                    })
                    self._response_started = True
                    
                    if data:
                        await send({
                            "type": "http.response.body",
                            "body": data,
                            "more_body": True,
                        })
            else:  # regular data chunk
                if not self._response_started:
                    await send({
                        "type": "http.response.start",
                        "status": self.status_code,
                        "headers": self.raw_headers,
                    })
                    self._response_started = True
                
                await send({
                    "type": "http.response.body",
                    "body": chunk,
                    "more_body": True,
                })
        
        await send({
            "type": "http.response.body",
            "body": b"",
            "more_body": False,
        })


@router.api_route("{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"])
async def messages(request: Request, path: str):
    target = settings.openai.api_base + path

    # 获取请求头
    headers = dict(request.headers)
    headers.pop("host", None)
    auth_key = headers.get("authorization", None)
    if auth_key is not None:
        if auth_key.startswith("Bearer "):
            auth_key = auth_key.removeprefix("Bearer ")
        if auth_key in child_key:
            headers["authorization"] = f"Bearer {settings.openai.api_key}"

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
