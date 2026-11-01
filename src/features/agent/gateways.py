from dataclasses import dataclass
from typing import Any, Protocol


class LLMGateway(Protocol):
    async def plan(self, query: str) -> dict: ...


class DatasetGateway(Protocol):
    async def all(self) -> list[dict]: ...


class FakeLLM:
    async def plan(self, query: str) -> dict:
        q = query.lower()
        out: dict[str, Any] = {"keywords": ["laptop"], "requirements": {}}
        if "render" in q:
            out["requirements"] = {"min_ram_gb": 16, "gpu": "dedicated"}
        if "uygun fiyat" in q:
            out["max_price"] = 40000
        return out


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
class Context:
    llm: LLMGateway
    dataset: DatasetGateway