from dataclasses import dataclass, field
from uuid import UUID
from features.agent.fsm import Step

@dataclass
class ContextDossier:
    job_id: UUID #search_job.id
    session_id: UUID #chat_session.id
    user_query: str
    round: int = 1
    events: list[dict] = field(default_factory=list)

    def add(self, kind: str, actor: str, step: Step | None = None,
            summary: str = "", public_message: str | None = None,
            data: dict | None = None) -> None:
        self.events.append({
            "seq": len(self.events) + 1, "kind": kind, "actor": actor,
            "step": step.value if step else None, "replan_round": self.round,
            "summary": summary, "public_message": public_message, "data": data or {},
        })

    def get(self, step: Step) -> dict | None:
        for e in reversed(self.events):
            if e["kind"] == "step_finished" and e["step"] == step.value:
                return e["data"]
        return None

    #context_dossier.get(Step.PLAN)      PLAN's output
    #context_dossier.get(Step.COLLECT)   COLLECT's output
    #context_dossier.get(Step.VALIDATE)  VALIDATE's output