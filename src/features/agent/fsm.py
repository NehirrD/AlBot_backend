#A list of steps and the possible transitions from one step to another
from enum import Enum

class Step(str, Enum):
    PLAN = "plan"
    COLLECT = "collect"
    VALIDATE = "validate"
    RANK = "rank"
    DONE = "done"
    FAILED = "failed"

#for permissions:
TRANSITIONS = {
    Step.PLAN: {Step.COLLECT, Step.FAILED},
    Step.COLLECT: {Step.VALIDATE, Step.FAILED},
    Step.VALIDATE: {Step.RANK, Step.PLAN, Step.FAILED},
    Step.RANK: {Step.DONE, Step.FAILED},
}
DEFAULT_NEXT = {Step.PLAN: Step.COLLECT, Step.COLLECT: Step.VALIDATE,
                Step.VALIDATE: Step.RANK, Step.RANK: Step.DONE}

def check(cur: Step, nxt: Step) -> None:
    if nxt not in TRANSITIONS.get(cur, set()):
        raise ValueError(f"illegal transition {cur.value} -> {nxt.value}")