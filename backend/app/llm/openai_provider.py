import time
from typing import Any, AsyncGenerator
from .base_provider import BaseLLMProvider, LLMResponse
from .config import LLMConfig

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

class OpenAIProvider(BaseLLMProvider):
    def __init__(self):
        self.api_key = LLMConfig.OPENAI_API_KEY
        if self.api_key:
            self.client = ChatOpenAI(model="gpt-4-turbo", api_key=self.api_key)
        else:
            self.client = None

    def _convert_to_lc_messages(self, formatted_prompt: Any):
        if isinstance(formatted_prompt, list):
            lc_messages = []
            for m in formatted_prompt:
                role = m.get("role", "user")
                content = m.get("content", "")
                if role == "system":
                    lc_messages.append(SystemMessage(content=content))
                elif role == "assistant":
                    lc_messages.append(AIMessage(content=content))
                else:
                    lc_messages.append(HumanMessage(content=content))
            return lc_messages
        elif isinstance(formatted_prompt, str):
            return [HumanMessage(content=formatted_prompt)]
        return [HumanMessage(content=str(formatted_prompt))]

    def generate_response(self, formatted_prompt: Any) -> LLMResponse:
        if not self.client:
            return LLMResponse(
                provider="openai",
                prompt_tokens=0,
                completion_tokens=0,
                total_tokens=0,
                response="OpenAI API Key not configured.",
                latency_ms=0.0
            )

        start_time = time.time()
        try:
            lc_messages = self._convert_to_lc_messages(formatted_prompt)
            response = self.client.invoke(lc_messages)
            latency_ms = (time.time() - start_time) * 1000

            prompt_tokens = 0
            completion_tokens = 0
            total_tokens = 0
            
            if hasattr(response, 'usage_metadata') and response.usage_metadata:
                prompt_tokens = response.usage_metadata.get('input_tokens', 0)
                completion_tokens = response.usage_metadata.get('output_tokens', 0)
                total_tokens = response.usage_metadata.get('total_tokens', 0)

            content = response.content if isinstance(response.content, str) else str(response.content)

            return LLMResponse(
                provider="openai",
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens,
                response=content,
                latency_ms=latency_ms
            )
        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            return LLMResponse(
                provider="openai",
                prompt_tokens=0,
                completion_tokens=0,
                total_tokens=0,
                response=f"Error generating OpenAI response: {str(e)}",
                latency_ms=latency_ms
            )

    async def stream_response(self, formatted_prompt: Any) -> AsyncGenerator[str, None]:
        yield "Streaming not yet implemented for OpenAI"

    def count_tokens(self, text: str) -> int:
        return len(text) // 4
