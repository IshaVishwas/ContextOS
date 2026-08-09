from typing import List, Dict, Any, Tuple
from .config import APCConfig

class TokenBudgetManager:
    def __init__(self):
        self.config = APCConfig
        self.max_tokens = self.config.MAX_TOKENS
        
    def estimate_tokens(self, text: str) -> int:
        return len(text) // self.config.CHARS_PER_TOKEN

    def allocate(
        self, 
        system_instructions: str, 
        user_query: str, 
        compressed_context: str, 
        recent_messages: List[Dict[str, str]]
    ) -> Tuple[str, List[Dict[str, str]], Dict[str, int]]:
        
        # 1. Protect system instructions and user query
        system_tokens = self.estimate_tokens(system_instructions)
        query_tokens = self.estimate_tokens(user_query)

        # 2. Allocate and Prune Memory
        memory_tokens = self.estimate_tokens(compressed_context)
        memory_budget = int(self.max_tokens * self.config.ALLOCATION["memory"])

        if memory_tokens > memory_budget:
            # Simple truncation from the bottom (assuming least important facts are at the end)
            allowed_chars = memory_budget * self.config.CHARS_PER_TOKEN
            compressed_context = compressed_context[:allowed_chars]
            memory_tokens = memory_budget

        # 3. Allocate and Prune Conversation
        # Need a copy to avoid mutating the original
        safe_messages = list(recent_messages)
        conversation_tokens = self.estimate_tokens(str(safe_messages))
        conv_budget = int(self.max_tokens * self.config.ALLOCATION["conversation"])

        if conversation_tokens > conv_budget:
            # Prune oldest messages first (keep latest)
            while self.estimate_tokens(str(safe_messages)) > conv_budget and len(safe_messages) > 0:
                safe_messages.pop(0)
            conversation_tokens = self.estimate_tokens(str(safe_messages))

        total_estimated = system_tokens + query_tokens + memory_tokens + conversation_tokens

        stats = {
            "system_tokens": system_tokens,
            "user_query_tokens": query_tokens,
            "memory_tokens": memory_tokens,
            "conversation_tokens": conversation_tokens,
            "estimated_tokens": total_estimated
        }

        return compressed_context, safe_messages, stats
