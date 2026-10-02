"""确认分派：确认请求必须显式选择原案或反案，按所选案改格表。

未选案、反案不存在或当前格表已不合法时抛 ConfirmError——任何 UPDATE 之前失败，格表不变。
"""
from app.engines.rota import apply_swap
from .detail import CHOICES, quad_of


class ConfirmError(Exception):
    def __init__(self, reason: str, status: int = 400):
        super().__init__(reason)
        self.reason = reason
        self.status = status


def select_proposal(body: dict | None) -> str:
    """从确认请求显式取所选案；未选案即失败。"""
    proposal = (body or {}).get("proposal")
    if proposal not in CHOICES:
        raise ConfirmError("proposal_required")
    return proposal


def apply_confirmation(c, sw: dict, proposal: str) -> dict:
    """按所选案执行交换，并把 selected 与 status 钉到同一笔记录。返回所施方案。"""
    if sw["status"] != "pending":
        raise ConfirmError("not_pending")
    q = quad_of(sw, proposal)
    if q is None:
        # 选了反案但从未提交过反案
        raise ConfirmError("counter_missing")

    assigns = [dict(r) for r in c.execute(
        "SELECT id,day,task_id,member_id FROM assignments WHERE week_id=?", (sw["week_id"],))]
    slots = [{"day": a["day"], "task_id": a["task_id"], "member_id": a["member_id"]} for a in assigns]
    try:
        new_slots = apply_swap(slots, q["a_day"], q["a_task"], q["b_day"], q["b_task"])
    except ValueError as e:
        raise ConfirmError(str(e))

    for a, s in zip(assigns, new_slots):
        c.execute("UPDATE assignments SET member_id=? WHERE id=?", (s["member_id"], a["id"]))
    c.execute("UPDATE swap_requests SET selected=?, status='confirmed' WHERE id=?",
              (proposal, sw["id"]))
    return {"swap_id": sw["id"], "selected": proposal, "applied": q}
