from uuid import uuid4
from fastapi import APIRouter
from pydantic import BaseModel
from features.agent.dossier import Dossier
from features.agent.gateways import Context, FakeDataset, FakeLLM
from features.agent.orchestrator import Orchestrator
from features.agent.steps.collect import CollectStep
from features.agent.steps.plan import PlanStep
from features.agent.steps.rank import RankStep
from features.agent.steps.validate import ValidateStep
from features.agent.fsm import Step
from features.agent.dtos import RunRequest
router = APIRouter(prefix="/agent", tags=["agent"])


@router.post("/run-demo")
async def run_demo(body: RunRequest):
    d = Dossier(job_id=uuid4(), session_id=uuid4(), user_query=body.query)
    ctx = Context(llm=FakeLLM(), dataset=FakeDataset())
    steps = [PlanStep(), CollectStep(), ValidateStep(), RankStep()]
    final = await Orchestrator(steps, ctx).run(d)
    return {
        "final_step": final,
        "recommendations": (d.get(Step.RANK) or {}).get("recommendations", []),
        #all dossier context:
        "events": d.events,
    }