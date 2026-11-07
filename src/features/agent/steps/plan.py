from features.agent.dtos import SearchFilters
from features.agent.fsm import Step
from core.agent.base import BaseStep, StepResult

class PlanStep(BaseStep):
    name = Step.PLAN

#context_tool_box llms tool box
    async def run(self, context_dossier, context_tool_box):
        raw = await context_tool_box.llm.plan(context_dossier.user_query)
        filters = SearchFilters(**raw)
        return StepResult(
            data={"filters": filters.model_dump(mode="json")},
            summary=f"filters: {filters.requirements}, max_price={filters.max_price}",
            public_message="I have analyzed your request and am searching for suitable laptops...",
        )