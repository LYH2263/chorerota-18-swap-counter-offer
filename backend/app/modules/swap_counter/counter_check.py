"""反案校验: counter four-tuple must be new and re-pass grid legality."""
from app.engines.rota import swap_legal

def validate_counter(slots: list[dict], original: dict,
                     a_day: int, a_task: int, b_day: int, b_task: int) -> dict:
    """A counter-proposal re-runs full swap legality on the live grid and must
    differ from the original four-tuple. On success the counter's two assignees
    are returned so the caller can freeze them alongside the tuple."""
    if (a_day, a_task, b_day, b_task) == (original["a_day"], original["a_task"],
                                          original["b_day"], original["b_task"]):
        return {"ok": False, "reason": "same_as_original"}
    return swap_legal(slots, a_day, a_task, b_day, b_task)
