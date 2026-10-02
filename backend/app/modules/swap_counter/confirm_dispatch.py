"""确认分派: an explicit case choice picks which four-tuple a confirm applies."""

ORIGINAL = "original"
COUNTER = "counter"

def resolve_case(swap: dict, selected: str | None) -> dict:
    """Confirm must name a case explicitly; the counter case requires a
    submitted counter. Returns the winning four-tuple without touching state."""
    if selected not in (ORIGINAL, COUNTER):
        return {"ok": False, "reason": "case_required"}
    if selected == ORIGINAL:
        return {"ok": True, "case": ORIGINAL,
                "tuple": (swap["a_day"], swap["a_task"], swap["b_day"], swap["b_task"])}
    if swap.get("c_a_day") is None:
        return {"ok": False, "reason": "no_counter"}
    return {"ok": True, "case": COUNTER,
            "tuple": (swap["c_a_day"], swap["c_a_task"], swap["c_b_day"], swap["c_b_task"])}
