import asyncio
from unittest.mock import AsyncMock, patch

from openai import APITimeoutError, APIConnectionError

from adapters.llm.llm_adapter import LLMAdapter
from adapters.llm.dtos.request_types import RequestType, Message
from adapters.llm.errors import (
    LLMTimeoutError,
    LLMConnectionError,
)


async def main():
    adapter = LLMAdapter()

    request = RequestType(
        model="mistralai/mistral-large-4-1t-a52b",
        messages=[Message(role="user", content="Merhaba!")],
    )

    try:
        # 1. Timeout error testi
        with patch.object(
            adapter.client.chat.completions,
            "create",
            new_callable=AsyncMock,
        ) as mock_create:

            mock_create.side_effect = APITimeoutError(request=None)

            try:
                await adapter.generate(request)
            except LLMTimeoutError:
                print("LLM timeout error test is successful!")
            else:
                raise AssertionError("LLMTimeoutError is expected but not raised.")

        # 2. Connection error testi
        with patch.object(
            adapter.client.chat.completions,
            "create",
            new_callable=AsyncMock,
        ) as mock_create:

            mock_create.side_effect = APIConnectionError(request=None)

            try:
                await adapter.generate(request)
            except LLMConnectionError:
                print("LLM connection error test is successful!")
            else:
                raise AssertionError("LLMConnectionError is expected but not raised.")

    finally:
        await adapter.client.close()


if __name__ == "__main__":
    asyncio.run(main())
