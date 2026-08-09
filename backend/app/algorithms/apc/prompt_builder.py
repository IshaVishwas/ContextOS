from typing import Dict, Any, List
from .interfaces import PromptPayload, APCResult
from .context_allocator import TokenBudgetManager
from .template_engine import PromptTemplateEngine

class AdaptivePromptBuilder:
    def __init__(self):
        self.allocator = TokenBudgetManager()
        self.engine = PromptTemplateEngine()

    def build_prompt(
        self, 
        user_query: str, 
        compressed_context: str, 
        recent_messages: List[Dict[str, str]], 
        system_instructions: str, 
        provider: str = "openai"
    ) -> APCResult:
        
        # 1. Allocate Budget and safely prune
        safe_context, safe_history, stats = self.allocator.allocate(
            system_instructions=system_instructions,
            user_query=user_query,
            compressed_context=compressed_context,
            recent_messages=recent_messages
        )

        # 2. Build Structured Payload
        payload = PromptPayload(
            system_prompt=system_instructions,
            compressed_context=safe_context,
            recent_messages=safe_history,
            user_query=user_query
        )

        # 3. Format using provider template
        formatted_prompt = self.engine.format(provider, payload)

        return APCResult(
            prompt_payload=payload,
            formatted_prompt=formatted_prompt,
            estimated_tokens=stats["estimated_tokens"],
            memory_tokens=stats["memory_tokens"],
            conversation_tokens=stats["conversation_tokens"],
            system_tokens=stats["system_tokens"],
            user_query_tokens=stats["user_query_tokens"]
        )

apc_engine = AdaptivePromptBuilder()
