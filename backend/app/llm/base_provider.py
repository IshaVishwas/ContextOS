from abc import ABC, abstractmethod
from typing import Any, AsyncGenerator
from pydantic import BaseModel

class LLMResponse(BaseModel):
    provider: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    response: str
    latency_ms: float

class BaseLLMProvider(ABC):
    @abstractmethod
    def generate_response(self, formatted_prompt: Any) -> LLMResponse:
        pass

    @abstractmethod
    def stream_response(self, formatted_prompt: Any) -> AsyncGenerator[str, None]:
        pass

    @abstractmethod
    def count_tokens(self, text: str) -> int:
        pass
