from abc import ABC, abstractmethod
from typing import Dict, Any, List
from pydantic import BaseModel

class PromptPayload(BaseModel):
    system_prompt: str
    compressed_context: str
    recent_messages: List[Dict[str, str]]
    user_query: str

class APCResult(BaseModel):
    prompt_payload: PromptPayload
    formatted_prompt: Any
    estimated_tokens: int
    memory_tokens: int
    conversation_tokens: int
    system_tokens: int
    user_query_tokens: int

class TemplateStrategy(ABC):
    @abstractmethod
    def format_prompt(self, payload: PromptPayload) -> Any:
        pass
