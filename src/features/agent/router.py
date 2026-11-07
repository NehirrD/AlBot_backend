from uuid import uuid4
from fastapi import APIRouter
from features.agent.context_dossier import ContextDossier
from features.agent.gateways import ContextToolBox, FakeDataset, FakeLLM
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
    context_dossier = ContextDossier(job_id=uuid4(), session_id=uuid4(), user_query=body.query)
    context_tool_box = ContextToolBox(llm=FakeLLM(), dataset=FakeDataset())
    steps = [PlanStep(), CollectStep(), ValidateStep(), RankStep()]
    final = await Orchestrator(steps, context_tool_box).run(context_dossier)
    return {
        "final_step": final,
        "recommendations": (context_dossier.get(Step.RANK) or {}).get("recommendations", []),
        #all context_dossier context:
        "events": context_dossier.events,
    }