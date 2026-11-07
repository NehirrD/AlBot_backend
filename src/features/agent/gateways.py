from dataclasses import dataclass
from typing import Any, Protocol
import json
import re
from adapters.llm.dtos.llm_request_dto import LLMRequestDto, Message
from adapters.llm.llm_base import BaseLLMAdapter
from features.agent.prompts import PLAN_SYSTEM_PROMPT

class LLMGateway(Protocol):
    async def plan(self, query: str) -> dict: ...


class DatasetGateway(Protocol):
    async def all(self) -> list[dict]: ...


class RealLLM:
    def __init__(self, adapter: BaseLLMAdapter):
        self.adapter = adapter

    async def plan(self, query: str) -> dict:
        request = LLMRequestDto(
            messages=[
                Message(role="system", content=PLAN_SYSTEM_PROMPT),
                Message(role="user", content=query),
            ],
            temperature=0.2,
            max_tokens=500,
        )
        response = await self.adapter.generate(request)
        return self._parse_json(response.content)

    @staticmethod
    def _parse_json(text: str) -> dict:
        text = re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.MULTILINE).strip()
        return json.loads(text)


class FakeDataset:
    _ROWS = [
        {"id": "1", "title": "Asus TUF F15 RTX 3050", "price": 38000, "ram_gb": 16, "gpu": "RTX 3050"},
        {"id": "2", "title": "Lenovo LOQ RTX 4050", "price": 42000, "ram_gb": 16, "gpu": "RTX 4050"},
        {"id": "3", "title": "MSI Katana RTX 4060", "price": 55000, "ram_gb": 32, "gpu": "RTX 4060"},
        {"id": "4", "title": "HP 250 G9 ofis", "price": 18000, "ram_gb": 8, "gpu": "integrated"},
        {"id": "5", "title": "Acer Aspire 5", "price": 25000, "ram_gb": 16, "gpu": "integrated"},
        {"id": "6", "title": "Monster Abra A5 RTX 3050", "price": 36000, "ram_gb": 8, "gpu": "RTX 3050"},
    ]

#It returns a copy of the list
    async def all(self) -> list[dict]:
        return list(self._ROWS)


@dataclass
class ContextToolBox:
    llm: LLMGateway
    dataset: DatasetGateway