from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from features.agent.dossier import Dossier
from features.agent.fsm import Step
from features.agent.gateways import Context

@dataclass
class StepResult:
    #it writes all data to context log -> it will improve
    data: dict = field(default_factory=dict)
    summary: str = ""
    public_message: str | None = None
    next: Step | None = None

class BaseStep(ABC):
    name: Step

    @abstractmethod
    async def run(self, dossier: Dossier, ctx: Context) -> StepResult: ...