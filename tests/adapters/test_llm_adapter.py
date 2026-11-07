import asyncio
from unittest.mock import AsyncMock, patch

from openai import APITimeoutError

from adapters.llm.dtos.llm_request_dto import LLMRequestDto, Message
from adapters.llm.errors import LLMTimeoutError
from adapters.llm.llm_adapter import LLMAdapter


async def main():
    adapter = LLMAdapter()
    print(adapter.default_model)

    request = LLMRequestDto(
        messages=[Message(role="user", content="Merhaba! Kendini kısaca tanıt.")],
        max_tokens=500,
    )

    try:
        with patch.object(
            adapter.client.chat.completions,
            "create",
            new_callable=AsyncMock,
        ) as mock_create:

            mock_create.side_effect = APITimeoutError(request=None)

            try:
                await adapter.generate(request)
            except LLMTimeoutError:
                print("LLM timeout error successfully raised and caught.")
            else:
                raise AssertionError("LLMTimeoutError is expected but not raised.")

    # request = LLMRequestDto(
    #     model="mistralai/mistral-large-4-1t-a52b",
    #     messages=[
    #         Message(
    #             role="system",
    #             content="Sen Türkçe cevap veren bir asistansın. Kısa ve açık cevap ver."
    #         ),
    #         Message(
    #             role="user",
    #             content="Merhaba! Kendini kısaca tanıt."
    #         )
    #     ],
    #     temperature=0.7,
    #     max_tokens=500
    # )

    # try:
    #     response = await adapter.generate(request)

    #     print("\nModel response:")
    #     print(response.content)

    #     print("\nUsed model:")
    #     print(response.model)

    #     print("\nToken usage")
    #     print("Prompt:", response.prompt_tokens)
    #     print("Completion:", response.completion_tokens)
    #     print("Total tokens:", response.total_tokens)

    finally:
        await adapter.close()


if __name__ == "__main__":
    asyncio.run(main())
