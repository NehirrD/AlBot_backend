from pydantic import BaseModel, Field


class LLMResponseDto(BaseModel):
    content: str
    model: str

    prompt_tokens: int | None = Field(default=None, ge=0)
    completion_tokens: int | None = Field(default=None, ge=0)
    total_tokens: int | None = Field(default=None, ge=0)
