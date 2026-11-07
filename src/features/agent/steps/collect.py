from features.agent.fsm import Step
from features.agent.steps.base import BaseStep, StepResult


class CollectStep(BaseStep):
    name = Step.COLLECT

    async def run(self, context_dossier, context_tool_box):
        products = await context_tool_box.dataset.all()
        return StepResult(
            data={"products": products},
            summary=f"{len(products)} products collected",
            public_message=f"{len(products)} I’ve found a few laptops; I’m checking it wheter it is suitable...",
        )