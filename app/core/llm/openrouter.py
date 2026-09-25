import time
import uuid
from collections.abc import Sequence

import httpx

from app.core.config import settings
from app.core.llm.errors import (
    LLMError,
    ModelAuthenticationError,
    ModelRateLimitError,
    ModelTimeoutError,
    ModelUnavailableError,
)
from app.core.llm.schemas import LLMResponse
from app.core.observability import tracer


def _parse_csv(value: str) -> tuple[str, ...]:
    return tuple(part.strip() for part in value.split(",") if part.strip())


class OpenRouterProvider:
    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        *,
        fallbacks: Sequence[str] = (),
        byok_providers: Sequence[str] = (),
        base_url: str | None = None,
        timeout: float | None = None,
    ):
        self._api_key = api_key if api_key is not None else settings.OPENROUTER_API_KEY
        self._model = model if model is not None else settings.OPENROUTER_MODEL
        self._fallbacks = fallbacks or _parse_csv(settings.OPENROUTER_FALLBACK_MODELS)
        self._byok_providers = byok_providers or _parse_csv(settings.OPENROUTER_BYOK_PROVIDERS)
        self._base_url = base_url or settings.OPENROUTER_BASE_URL
        self._timeout = timeout if timeout is not None else settings.OPENROUTER_TIMEOUT_SECONDS

    @property
    def model(self) -> str:
        return self._model

    async def generate(self, prompt: str) -> LLMResponse:
        with tracer.start_as_current_span("llm.openrouter.generate") as span:
            if not self._api_key:
                raise ModelAuthenticationError(
                    "OPENROUTER_API_KEY is not configured. Set it in the environment."
                )

            request_id = str(uuid.uuid4())
            url = f"{self._base_url}/chat/completions"
            headers = {
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "http://localhost:5173",
                "X-Title": "AI Knowledge Base",
            }
            payload: dict = {
                "model": self._model,
                "messages": [{"role": "user", "content": prompt}],
            }
            if self._byok_providers:
                payload["provider"] = {"only": list(self._byok_providers)}
            elif self._fallbacks:
                payload["models"] = list(self._fallbacks)

            span.set_attribute("llm.model", self._model)
            span.set_attribute("llm.request_id", request_id)

            start = time.perf_counter()
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                try:
                    http_response = await client.post(url, headers=headers, json=payload)
                except httpx.TimeoutException as exc:
                    raise ModelTimeoutError(
                        f"Request {request_id} timed out after {self._timeout}s."
                    ) from exc
                except httpx.RequestError as exc:
                    raise ModelUnavailableError(
                        f"Request {request_id} network error: {exc}"
                    ) from exc

            latency_ms = (time.perf_counter() - start) * 1000
            self._raise_for_status(http_response, request_id)
            parsed = self._parse_response(http_response, request_id, latency_ms)

            usage = parsed.usage or {}
            span.set_attribute("llm.latency_ms", parsed.latency_ms)
            if "prompt_tokens" in usage:
                span.set_attribute("llm.prompt_tokens", usage["prompt_tokens"])
            if "completion_tokens" in usage:
                span.set_attribute("llm.completion_tokens", usage["completion_tokens"])
            if "total_tokens" in usage:
                span.set_attribute("llm.total_tokens", usage["total_tokens"])

            return parsed

    def _raise_for_status(self, http_response: httpx.Response, request_id: str) -> None:
        status = http_response.status_code
        if status == 200:
            return
        detail = http_response.text.strip()[:400]
        suffix = f" {detail}" if detail else ""
        if status == 401:
            raise ModelAuthenticationError(
                f"Request {request_id}: Unauthorized (401). Check OPENROUTER_API_KEY.{suffix}"
            )
        if status == 429:
            raise ModelRateLimitError(f"Request {request_id}: Rate limited (429).{suffix}")
        if status >= 500:
            raise ModelUnavailableError(
                f"Request {request_id}: Server error ({status}).{suffix}"
            )
        raise LLMError(
            f"Request {request_id}: Unexpected response ({status}): {http_response.text}"
        )

    def _parse_response(
        self,
        http_response: httpx.Response,
        request_id: str,
        latency_ms: float,
    ) -> LLMResponse:
        try:
            data = http_response.json()
        except ValueError as exc:
            raise LLMError(f"Request {request_id}: Response was not valid JSON.") from exc

        if isinstance(data, dict) and "error" in data and "choices" not in data:
            error = data["error"]
            message = str(error.get("message") if isinstance(error, dict) else error)
            if "rate" in message.lower():
                raise ModelRateLimitError(f"Request {request_id}: {message}")
            raise ModelUnavailableError(f"Request {request_id}: {message}")

        try:
            content = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise LLMError(
                f"Request {request_id}: Could not parse response (missing choices)."
            ) from exc

        if not isinstance(content, str):
            raise LLMError(f"Request {request_id}: Model returned non-text content.")

        return LLMResponse(
            request_id=request_id,
            model=str(data.get("model", self._model)),
            response=content,
            usage=data.get("usage") or {},
            latency_ms=latency_ms,
        )
