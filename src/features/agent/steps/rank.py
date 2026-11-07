from features.agent.fsm import Step
from core.agent.base import BaseStep, StepResult


class RankStep(BaseStep):
    name = Step.RANK

    async def run(self, context_dossier, context_tool_box):
        products = context_dossier.get(Step.VALIDATE)["products"]
        best = sorted(products, key=lambda p: (-p["ram_gb"], p["price"]))[:3]
        recs = [
            {"rank": i, "product": p,
             "reason": f"{p['ram_gb']} GB RAM, {p['gpu']}, {p['price']} TL"}
            for i, p in enumerate(best, start=1)
        ]
        return StepResult(
            data={"recommendations": recs},
            summary=f"{len(recs)} recommendations",
            public_message=f"İşte sana en uygun {len(recs)} laptop:",
        )