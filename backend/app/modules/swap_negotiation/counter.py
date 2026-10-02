"""反案校验：pending 对调由对方提交一套新四元组，须重新过合法性并冻结反案双方成员。

反案非法时抛 CounterError，调用方不落库——原 pending 与原案四元组均不变。
"""
from app.engines.rota import swap_legal

class CounterError(Exception):
    def __init__(self, reason: str, status: int = 400):
        super().__init__(reason)
        self.reason = reason
        self.status = status


def counter_quad(body: dict) -> dict:
    """从请求体取反案四元组，缺字段/类型不对即非法。"""
    try:
        return {
            "a_day": int(body["a_day"]), "a_task": int(body["a_task"]),
            "b_day": int(body["b_day"]), "b_task": int(body["b_task"]),
        }
    except (KeyError, TypeError, ValueError):
        raise CounterError("counter_quad_invalid")


def validate_counter(c, sw: dict, body: dict) -> dict:
    """对 pending 对调校验反案，返回四元组 + 冻结成员；全部校验先于任何写操作。"""
    if sw["status"] != "pending":
        raise CounterError("not_pending")
    quad = counter_quad(body or {})

    slots = [dict(r) for r in c.execute(
        "SELECT day,task_id,member_id FROM assignments WHERE week_id=?", (sw["week_id"],))]
    check = swap_legal(slots, quad["a_day"], quad["a_task"], quad["b_day"], quad["b_task"])
    if not check["ok"]:
        # 反案非法：不覆盖原案、不改原 pending
        raise CounterError(check["reason"])

    quad["a_member"] = check["a_member"]   # 冻结反案双方成员快照
    quad["b_member"] = check["b_member"]
    proposed_by = (body or {}).get("proposed_by")
    quad["proposed_by"] = int(proposed_by) if proposed_by is not None else None
    return quad


def persist_counter(c, swap_id: int, q: dict) -> None:
    """把反案四元组与成员快照写到 pending 单上（原案列不动）。"""
    c.execute(
        """UPDATE swap_requests
           SET ca_day=?, ca_task=?, cb_day=?, cb_task=?, ca_member=?, cb_member=?, proposed_by=?
           WHERE id=?""",
        (q["a_day"], q["a_task"], q["b_day"], q["b_task"],
         q["a_member"], q["b_member"], q["proposed_by"], swap_id))
