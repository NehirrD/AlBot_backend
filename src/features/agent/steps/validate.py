from features.agent.fsm import Step
from features.agent.steps.base import BaseStep, StepResult


class ValidateStep(BaseStep):
    name = Step.VALIDATE

    async def run(self, context_dossier, context_tool_box):
        filters = context_dossier.get(Step.PLAN)["filters"]
        products = context_dossier.get(Step.COLLECT)["products"]
        req = filters["requirements"]
        max_price = filters["max_price"]
        valid = []
        for p in products:
            if max_price is not None and p["price"] > max_price:
                continue
            if p["ram_gb"] < req.get("min_ram_gb", 0):
                continue
            if req.get("gpu") == "dedicated" and p["gpu"] == "integrated":
                continue
            valid.append(p)

        return StepResult(
            data={"products": valid},
            summary=f"{len(valid)} of {len(products)} products passed",
            public_message=f"{len(valid)} laptop kriterlerine uyuyor, sıralıyorum...",
        )