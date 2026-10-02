"""对调详情双案投影：原案四元组/成员快照与反案并列可查，所选案字段同钉。"""

ORIGINAL = "original"
COUNTER = "counter"
CHOICES = (ORIGINAL, COUNTER)


def quad_of(sw: dict, proposal: str) -> dict | None:
    """取某一案的标准四元组 + 冻结成员；反案尚未提交时返回 None。"""
    if proposal == ORIGINAL:
        return {
            "a_day": sw["a_day"], "a_task": sw["a_task"],
            "b_day": sw["b_day"], "b_task": sw["b_task"],
            "a_member": sw["a_member"], "b_member": sw["b_member"],
        }
    if proposal == COUNTER:
        if sw["ca_day"] is None:
            return None
        return {
            "a_day": sw["ca_day"], "a_task": sw["ca_task"],
            "b_day": sw["cb_day"], "b_task": sw["cb_task"],
            "a_member": sw["ca_member"], "b_member": sw["cb_member"],
        }
    return None


def _projection(sw: dict, proposal: str, names: dict | None) -> dict | None:
    q = quad_of(sw, proposal)
    if q is None:
        return None
    if names:
        q = dict(q)
        q["a_member_name"] = names.get(q["a_member"], "?")
        q["b_member_name"] = names.get(q["b_member"], "?")
    return q


def project_swap(sw: dict, names: dict | None = None) -> dict:
    """原案/反案双案投影；selected 与 applied 始终指向同一案。"""
    selected = sw["selected"]
    out = {
        "id": sw["id"],
        "week_id": sw["week_id"],
        "status": sw["status"],
        "note": sw["note"],
        "proposed_by": sw["proposed_by"],
        "original": _projection(sw, ORIGINAL, names),
        "counter": _projection(sw, COUNTER, names),
        "selected": selected,
        "applied": _projection(sw, selected, names) if selected in CHOICES else None,
    }
    return out
