import httpx
import json
import time
from typing import Dict, Any, Optional
from ..config import settings


class OpenAIService:
    def __init__(self):
        # self.api_key = settings.openai_api_key
        # self.api_base = settings.openai_api_base
        # self.headers = {
        #     "Authorization": f"Bearer {self.api_key}",
        #     "Content-Type": "application/json"
        # }
        pass
    
    async def chat_completion(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        调用 OpenAI 的聊天补全 API
        """
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self.api_base}/chat/completions",
                headers=self.headers,
                json=request_data
            )
            
            if response.status_code != 200:
                return {
                    "error": {
                        "message": f"OpenAI API 错误: {response.text}",
                        "type": "api_error",
                        "code": response.status_code
                    }
                }
            
            return response.json()