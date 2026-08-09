from typing import Dict, Any, List
from .interfaces import TemplateStrategy, PromptPayload

class OpenAITemplate(TemplateStrategy):
    def format_prompt(self, payload: PromptPayload) -> List[Dict[str, str]]:
        messages = []
        
        system_content = f"{payload.system_prompt}\n\nContext:\n{payload.compressed_context}"
        messages.append({"role": "system", "content": system_content})
        
        for msg in payload.recent_messages:
            messages.append({"role": msg.get("role", "user"), "content": msg.get("content", "")})
            
        messages.append({"role": "user", "content": payload.user_query})
        
        return messages

class GeminiTemplate(TemplateStrategy):
    def format_prompt(self, payload: PromptPayload) -> str:
        prompt = f"**System Instructions**\n{payload.system_prompt}\n\n"
        prompt += f"**Background Context**\n{payload.compressed_context}\n\n"
        prompt += "**Conversation History**\n"
        for msg in payload.recent_messages:
            prompt += f"{msg.get('role', 'user').capitalize()}: {msg.get('content', '')}\n"
        
        prompt += f"\n**User Request**\n{payload.user_query}\n"
        return prompt

class AnthropicTemplate(TemplateStrategy):
    def format_prompt(self, payload: PromptPayload) -> str:
        prompt = f"<system>\n{payload.system_prompt}\n</system>\n\n"
        prompt += f"<context>\n{payload.compressed_context}\n</context>\n\n"
        prompt += "<history>\n"
        for msg in payload.recent_messages:
            role = msg.get("role", "user")
            prompt += f"<{role}>{msg.get('content', '')}</{role}>\n"
        prompt += "</history>\n\n"
        prompt += f"<query>\n{payload.user_query}\n</query>"
        return prompt

class PromptTemplateEngine:
    def __init__(self):
        self.strategies = {
            "openai": OpenAITemplate(),
            "gemini": GeminiTemplate(),
            "anthropic": AnthropicTemplate()
        }

    def format(self, provider: str, payload: PromptPayload) -> Any:
        strategy = self.strategies.get(provider.lower())
        if not strategy:
            raise ValueError(f"Provider {provider} not supported.")
        return strategy.format_prompt(payload)
