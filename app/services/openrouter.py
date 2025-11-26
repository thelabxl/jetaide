import httpx

from app.core.config import settings


class OpenRouterService:
    """Service to interact with OpenRouter API with dynamic model selection based on pricing."""

    def __init__(self):
        self.base_url = settings.openrouter_base_url
        self.api_key = settings.openrouter_api_key
        self._models_cache: list[dict] | None = None

    async def get_models(self, refresh: bool = False) -> list[dict]:
        """Fetch available models from OpenRouter with their pricing."""
        if self._models_cache and not refresh:
            return self._models_cache

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/models",
                headers={"Authorization": f"Bearer {self.api_key}"},
            )
            response.raise_for_status()
            data = response.json()
            self._models_cache = data.get("data", [])
            return self._models_cache

    async def get_best_model(
        self,
        max_price_per_million: float = 5.0,
        min_context_length: int = 8000,
        prefer_providers: list[str] | None = None,
    ) -> str:
        """
        Select the best model based on pricing and capabilities.

        Args:
            max_price_per_million: Maximum price per million tokens (input + output avg)
            min_context_length: Minimum context length required
            prefer_providers: List of preferred providers (e.g., ["anthropic", "openai"])

        Returns:
            Model ID string for the selected model
        """
        models = await self.get_models()

        # Filter models by context length
        eligible = [
            m for m in models
            if m.get("context_length", 0) >= min_context_length
        ]

        # Calculate average price and filter by max price
        def avg_price(model: dict) -> float:
            pricing = model.get("pricing", {})
            prompt = float(pricing.get("prompt", "999"))
            completion = float(pricing.get("completion", "999"))
            return (prompt + completion) / 2

        eligible = [m for m in eligible if avg_price(m) <= max_price_per_million / 1_000_000]

        if not eligible:
            # Fallback to a known good model
            return "anthropic/claude-3.5-sonnet"

        # Sort by preferred providers first, then by price
        def sort_key(model: dict) -> tuple:
            provider = model.get("id", "").split("/")[0]
            is_preferred = 0 if prefer_providers and provider in prefer_providers else 1
            return (is_preferred, avg_price(model))

        eligible.sort(key=sort_key)
        return eligible[0]["id"]

    async def chat(
        self,
        messages: list[dict],
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> str:
        """
        Send a chat completion request to OpenRouter.

        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Model ID to use (if None, will auto-select best model)
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response

        Returns:
            Assistant's response text
        """
        if model is None:
            model = await self.get_best_model()

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "HTTP-Referer": settings.backend_url,
                    "X-Title": "JetAide",
                },
                json={
                    "model": model,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                },
                timeout=60.0,
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]

    async def chat_stream(
        self,
        messages: list[dict],
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ):
        """
        Stream a chat completion response from OpenRouter.

        Yields:
            Chunks of the assistant's response text
        """
        if model is None:
            model = await self.get_best_model()

        async with httpx.AsyncClient() as client:
            async with client.stream(
                "POST",
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "HTTP-Referer": settings.backend_url,
                    "X-Title": "JetAide",
                },
                json={
                    "model": model,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    "stream": True,
                },
                timeout=60.0,
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data = line[6:]
                        if data == "[DONE]":
                            break
                        import json
                        chunk = json.loads(data)
                        delta = chunk.get("choices", [{}])[0].get("delta", {})
                        if content := delta.get("content"):
                            yield content


openrouter_service = OpenRouterService()
