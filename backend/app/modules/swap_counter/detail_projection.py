"""详情双案投影: original case + counter case + selected_case in one view."""

def project_detail(swap: dict) -> dict:
    """The original four-tuple and member snapshot stay queryable forever;
    the counter case (tuple + frozen members) appears once submitted."""
    detail = {
        "id": swap["id"],
        "week_id": swap["week_id"],
        "status": swap["status"],
        "note": swap["note"],
        "selected_case": swap["selected_case"],
        "original": {
            "a_day": swap["a_day"], "a_task": swap["a_task"],
            "b_day": swap["b_day"], "b_task": swap["b_task"],
            "a_member": swap["a_member"], "b_member": swap["b_member"],
        },
        "counter": None,
    }
    if swap["c_a_day"] is not None:
        detail["counter"] = {
            "a_day": swap["c_a_day"], "a_task": swap["c_a_task"],
            "b_day": swap["c_b_day"], "b_task": swap["c_b_task"],
            "a_member": swap["c_a_member"], "b_member": swap["c_b_member"],
        }
    return detail
