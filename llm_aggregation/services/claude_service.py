import traceback

import httpx
from typing import Dict, Any, Optional

from anthropic import AnthropicBedrock, AsyncAnthropic, NOT_GIVEN
from httpx import Proxy

from ..config import settings, ClaudeConfig
from ..logger import logger


def init_client(c: ClaudeConfig):
    if c is None:
        return None
    if c.bedrock is not None:
        http_client = None
        if c.proxy is not None:
            http_client = httpx.Client(proxy=Proxy(url=c.proxy))

        return AnthropicBedrock(aws_secret_key=c.bedrock.secret_key,
                                aws_access_key=c.bedrock.access_key,
                                aws_region=c.bedrock.region,
                                http_client=http_client
                                )
    else:
        http_client = None
        if c.proxy is not None:
            http_client = httpx.AsyncClient(proxy=Proxy(url=c.proxy))
        return AsyncAnthropic(api_key=c.api_key, auth_token=c.auth_token, base_url=c.api_base, http_client=http_client)


class ClaudeService:
    def __init__(self):
        self.x = AsyncAnthropic()
        self.config = settings.claude
        self.client = init_client(self.config)

    def check_key(self, key: str) -> bool:
        return self.config.api_key == key

    async def streaming_messages(self, request_data: Dict[str, Any]):
        try:
            m = request_data.get("messages", [])
            max_tokens = request_data.get("max_tokens", 4096)
            model: str = request_data.get("model")
            thinking_config = request_data.get("thinking", NOT_GIVEN)
            temperature = request_data.get("temperature", NOT_GIVEN)
            if self.config.bedrock is not None:
                if model.endswith("thinking"):
                    thinking_config = {
                        "budget_tokens": max_tokens - 1,
                        "type": 'enabled'
                    }
                    temperature = 1

                model = self.config.bedrock.model_mapping.get(model)

            with self.client.messages.stream(max_tokens=max_tokens,
                                             messages=m,
                                             model=model,
                                             metadata=request_data.get("metadata", NOT_GIVEN),
                                             stop_sequences=request_data.get("stop_sequences", NOT_GIVEN),
                                             system=request_data.get("metadata", NOT_GIVEN),
                                             temperature=temperature,
                                             top_k=request_data.get("top_k", NOT_GIVEN),
                                             top_p=request_data.get("top_p", NOT_GIVEN),
                                             thinking=thinking_config,
                                             tool_choice=request_data.get("tool_choice", NOT_GIVEN),
                                             tools=request_data.get("tools", NOT_GIVEN),
                                             ) as stream:
                for event in stream:
                    msg = f"event: {event.type}\ndata: {event.model_dump_json()}\n\n"
                    logger.info(msg)
                    if event.type not in self.config.bedrock.event_types:
                        continue

                    yield msg
        except Exception as e:
            print(e)
            traceback.print_exc()
            pass

    async def messages(self, request_data: Dict[str, Any]) -> dict[str, Any]:
        m = request_data.get("messages", [])
        max_tokens = request_data.get("max_tokens", 4096)
        model: str = request_data.get("model")
        thinking_config = request_data.get("thinking", NOT_GIVEN)
        temperature = request_data.get("temperature", NOT_GIVEN)
        if self.config.bedrock is not None:
            if model.endswith("thinking"):
                thinking_config = {
                    "budget_tokens": max_tokens - 1,
                    "type": 'enabled'
                }
                temperature = 1

            model = self.config.bedrock.model_mapping.get(model)
        try:
            message = self.client.messages.create(
                max_tokens=max_tokens,
                messages=m,
                model=model,
                metadata=request_data.get("metadata", NOT_GIVEN),
                stop_sequences=request_data.get("stop_sequences", NOT_GIVEN),
                system=request_data.get("metadata", NOT_GIVEN),
                temperature=temperature,
                top_k=request_data.get("top_k", NOT_GIVEN),
                top_p=request_data.get("top_p", NOT_GIVEN),
                thinking=thinking_config,
                tool_choice=request_data.get("tool_choice", NOT_GIVEN),
                tools=request_data.get("tools", NOT_GIVEN),
            )
            ret = message.model_dump()

            json_str = message.model_dump_json()
            logger.info(json_str)
            return ret
        except Exception as e:
            print(e)
            traceback.print_exc()
            return {"error": str(e)}

    def get_models(self):
        data = []
        if self.config.bedrock is not None:
            for key in self.config.bedrock.model_mapping.keys():
                data.append(
                    {
                        "created_at": "2025-02-19T00:00:00Z",
                        "display_name": key,
                        "id": key,
                        "type": "model"
                    }
                )

        return {
            "data": data,
            "first_id": None,
            "has_more": False,
            "last_id": None
        }
