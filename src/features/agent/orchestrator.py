from features.agent.context_dossier import ContextDossier
from features.agent.fsm import DEFAULT_NEXT, Step, check
from features.agent.gateways import ContextToolBox
from core.agent.base import BaseStep

class Orchestrator:
    def __init__(self, steps: list[BaseStep], context_tool_box: ContextToolBox):
        self.steps = {s.name: s for s in steps}
        self.context_tool_box = context_tool_box

    async def run(self, context_dossier: ContextDossier) -> Step:
        context_dossier.add("user_message", "user", summary=context_dossier.user_query)
        #When continue from checkpoint is added, this will become the current_step in the DB.
        current = Step.PLAN
        while current not in (Step.DONE, Step.FAILED):
            step = self.steps.get(current)
            if step is None:
                context_dossier.add("decision", "orchestrator", current,
                                    summary=f"{current.value} not implemented, stopping")
                break
            context_dossier.add("step_started", "orchestrator", current)
            try:
                result = await step.run(context_dossier, self.context_tool_box)
                context_dossier.add("step_finished", "orchestrator", current,
                                    result.summary, result.public_message, result.data)
                nxt = result.next or DEFAULT_NEXT[current]
                #FSM control:
                check(current, nxt)
            except Exception as e:
                context_dossier.add("error", "orchestrator", current, summary=str(e))
                return Step.FAILED
            current = nxt
        return current