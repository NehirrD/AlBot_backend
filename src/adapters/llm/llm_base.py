from abc import ABC, abstractmethod

from adapters.llm.dtos.llm_request_dto import LLMRequestDto
from adapters.llm.dtos.llm_response_dto import LLMResponseDto


class BaseLLMAdapter(ABC):
    """
    Base class for LLM adapters.
    """

    @abstractmethod
    async def generate(self, request: LLMRequestDto) -> LLMResponseDto:
        """
        Generates a response from the LLM based on the provided request.
        """
