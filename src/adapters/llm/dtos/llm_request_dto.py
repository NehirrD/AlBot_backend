from typing import Literal

from pydantic import BaseModel, Field


class Message(BaseModel):
    """
    Message is a Pydantic model that represents the structure of a message.
    It includes the following fields:
    - role: The role of the message (string).
    - content: The content of the message (string).
    """

    role: Literal["system", "user", "assistant"]
    content: str


class LLMRequestDto(BaseModel):
    """
    LLMRequestDto is a Pydantic model that represents the structure of an LLM request.
    It includes the following fields:
    - messages: The messages for the request (list of Message objects).
    - model: The model to use for the request (string).
    - temperature: The temperature for the request (float).
    - max_tokens: The maximum number of tokens for the request (int).
    """

    messages: list[Message]
    model: str | None = Field(default=None)
    temperature: float = Field(default=0.7, ge=0, le=2)
    max_tokens: int = Field(default=1000, gt=0)
