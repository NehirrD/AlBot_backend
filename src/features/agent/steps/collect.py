from features.agent.fsm import Step
from features.agent.steps.base import BaseStep, StepResult


class CollectStep(BaseStep):
    name = Step.COLLECT

    async def run(self, dossier, ctx):
        products = await ctx.dataset.all()
        return StepResult(
            data={"products": products},
            summary=f"{len(products)} products collected",
            public_message=f"{len(products)} I’ve found a few laptops; I’m checking it wheter it is suitable...",
        )