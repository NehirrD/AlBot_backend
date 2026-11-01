# Listens to the LLM queue and runs the ranking step of a search as a separate background process.

from openai import (
    AsyncOpenAI,
    APIConnectionError,
    APITimeoutError,
    APIStatusError,
    RateLimitError,
    AuthenticationError,
)

# from openai import AsyncOpenAI
from core.config import llm_settings  # settings

from adapters.llm.dtos.request_types import RequestType
from adapters.llm.dtos.response_types import ResponseType
from adapters.llm.errors import (
    LLMConnectionError,
    LLMTimeoutError,
    LLMResponseError,
)


class LLMAdapter:
    """Handles communication with external LLM providers."""

    def __init__(self):
        self.client = AsyncOpenAI(
            base_url=llm_settings.NVIDIA_BASE_URL,
            api_key=llm_settings.NVIDIA_API_KEY,
        )

        self.default_model = llm_settings.LLM_MODEL

    async def generate(self, request: RequestType) -> ResponseType:
        """Generates a response from the LLM based on the provided request."""
        try:
            response = await self.client.chat.completions.create(
                model=request.model or self.default_model,
                messages=[message.model_dump() for message in request.messages],
                temperature=request.temperature,
                max_tokens=request.max_tokens,
            )

            choice = response.choices[0]
            content = choice.message.content

            if not content:
                raise LLMResponseError("LLM is empty or returned an invalid response.")

            return ResponseType(
                content=content,
                model=response.model,
                prompt_tokens=response.usage.prompt_tokens if response.usage else None,
                completion_tokens=(
                    response.usage.completion_tokens if response.usage else None
                ),
                total_tokens=response.usage.total_tokens if response.usage else None,
            )
        except LLMResponseError:
            raise

        except APITimeoutError as error:
            raise LLMTimeoutError(
                "LLM API request timed out. Please try again later."
            ) from error

        except APIConnectionError as error:
            raise LLMConnectionError(
                "LLM API connection error. Please check your network connection."
            ) from error

        except RateLimitError as error:
            raise LLMAdapterError("LLM API usage limit exceeded.") from error

        except AuthenticationError as error:
            raise LLMAdapterError("LLM API authentication failed.") from error

        except APIStatusError as error:
            raise LLMAdapterError(f"LLM API error code: {error.status_code}") from error

        except Exception as error:
            raise LLMAdapterError(f"Unexpected LLM error: {error}") from error

    async def close(self) -> None:
        await self.client.close()
