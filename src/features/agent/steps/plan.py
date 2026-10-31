from features.agent.dtos import SearchFilters
from features.agent.fsm import Step
from features.agent.steps.base import BaseStep, StepResult

class PlanStep(BaseStep):
    name = Step.PLAN

#ctx llms tool box
    async def run(self, dossier, ctx):
        raw = await ctx.llm.plan(dossier.user_query)
        filters = SearchFilters(**raw)
        return StepResult(
            data={"filters": filters.model_dump(mode="json")},
            summary=f"filters: {filters.requirements}, max_price={filters.max_price}",
            public_message="I have analyzed your request and am searching for suitable laptops...",
        )