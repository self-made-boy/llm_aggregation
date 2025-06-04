from fastapi.responses import StreamingResponse
from typing import AsyncGenerator, Any


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