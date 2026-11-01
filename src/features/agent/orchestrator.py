from features.agent.dossier import Dossier
from features.agent.fsm import DEFAULT_NEXT, Step, check
from features.agent.gateways import Context
from features.agent.steps.base import BaseStep

class Orchestrator:
    def __init__(self, steps: list[BaseStep], ctx: Context):
        self.steps = {s.name: s for s in steps}
        self.ctx = ctx

    async def run(self, dossier: Dossier) -> Step:
        dossier.add("user_message", "user", summary=dossier.user_query)
        #When continue from checkpoint is added, this will become the current_step in the DB.
        current = Step.PLAN
        while current not in (Step.DONE, Step.FAILED):
            step = self.steps.get(current)
            if step is None:
                dossier.add("decision", "orchestrator", current,
                            summary=f"{current.value} not implemented, stopping")
                break
            dossier.add("step_started", "orchestrator", current)
            try:
                result = await step.run(dossier, self.ctx)
                dossier.add("step_finished", "orchestrator", current,
                            result.summary, result.public_message, result.data)
                nxt = result.next or DEFAULT_NEXT[current]
                #FSM control:
                check(current, nxt)
            except Exception as e:
                dossier.add("error", "orchestrator", current, summary=str(e))
                return Step.FAILED
            current = nxt
        return current