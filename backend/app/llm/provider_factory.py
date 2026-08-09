from .base_provider import BaseLLMProvider
from .openai_provider import OpenAIProvider
from .gemini_provider import GeminiProvider
from .anthropic_provider import AnthropicProvider

class ProviderFactory:
    @staticmethod
    def get_provider(name: str) -> BaseLLMProvider:
        name = name.lower()
        if name == "openai":
            return OpenAIProvider()
        elif name == "gemini":
            return GeminiProvider()
        elif name == "anthropic":
            return AnthropicProvider()
        else:
            raise ValueError(f"Unknown provider: {name}")
