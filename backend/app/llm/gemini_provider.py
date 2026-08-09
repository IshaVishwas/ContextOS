import time
from typing import Any, AsyncGenerator
from .base_provider import BaseLLMProvider, LLMResponse
from .config import LLMConfig

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

class GeminiProvider(BaseLLMProvider):
    def __init__(self):
        self.api_key = LLMConfig.GEMINI_API_KEY
        if self.api_key:
            self.client = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=self.api_key)
        else:
            self.client = None

    def generate_response(self, formatted_prompt: Any) -> LLMResponse:
        if not self.client:
            return LLMResponse(
                provider="gemini",
                prompt_tokens=0,
                completion_tokens=0,
                total_tokens=0,
                response="Gemini API Key not configured. Prompt would have been:\n" + str(formatted_prompt),
                latency_ms=0.0
            )

        start_time = time.time()
        try:
            prompt_str = str(formatted_prompt)
            response = self.client.invoke([HumanMessage(content=prompt_str)])
            latency_ms = (time.time() - start_time) * 1000

            prompt_tokens = 0
            completion_tokens = 0
            total_tokens = 0

            if hasattr(response, 'usage_metadata') and response.usage_metadata:
                prompt_tokens = response.usage_metadata.get('input_tokens', 0)
                completion_tokens = response.usage_metadata.get('output_tokens', 0)
                total_tokens = response.usage_metadata.get('total_tokens', 0)

            if total_tokens == 0:
                prompt_tokens = len(prompt_str) // 4
                completion_tokens = len(str(response.content)) // 4
                total_tokens = prompt_tokens + completion_tokens

            content = response.content if isinstance(response.content, str) else str(response.content)

            return LLMResponse(
                provider="gemini",
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens,
                response=content,
                latency_ms=latency_ms
            )
        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            return LLMResponse(
                provider="gemini",
                prompt_tokens=0,
                completion_tokens=0,
                total_tokens=0,
                response=f"Error generating Gemini response: {str(e)}",
                latency_ms=latency_ms
            )

    async def stream_response(self, formatted_prompt: Any) -> AsyncGenerator[str, None]:
        if not self.client:
            yield "Gemini API Key not configured."
            return

        try:
            prompt_str = str(formatted_prompt)
            for chunk in self.client.stream([HumanMessage(content=prompt_str)]):
                if chunk.content:
                    yield str(chunk.content)
        except Exception as e:
            yield f"Error in stream: {str(e)}"

    def count_tokens(self, text: str) -> int:
        return len(text) // 4
