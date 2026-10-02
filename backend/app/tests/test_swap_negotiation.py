"""反提案链路：选反案确认 / 选原案确认 / 反案非法不改原 pending / 未选案确认失败。"""
import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("DATA_DIR", str(tmp_path))
    from app import seed
    from app.main import app
    seed.init_db()  # 预置 3 名 clean 成员、3 个正权重任务、第 1 周
    with TestClient(app) as c:
        r = c.post("/api/weeks/1/generate", json={"days": 7})
        assert r.status_code == 200
        yield c


def board_map(client):
    assigns = client.get("/api/weeks/1/board").json()["assignments"]
    return {(a["day"], a["task_id"]): a["member_id"] for a in assigns}


def make_swap(client, a=(0, 1), b=(0, 2)):
    r = client.post("/api/weeks/1/swaps", json={
        "a_day": a[0], "a_task": a[1], "b_day": b[0], "b_task": b[1]})
    assert r.status_code == 200, r.text
    return r.json()["id"]


# 网格按任务列轮转：(day,1)=阿明1 (day,2)=小雨2 (day,3)=爷爷3
ORIG = ((0, 1), (0, 2))   # 成员 1 ↔ 2
COUNTER = ((1, 1), (1, 2))  # 同样是成员 1 ↔ 2，但落在另一行
ILLEGAL = ((0, 1), (1, 1))  # 两格都是成员 1 → same_assignee


def test_confirm_counter_applies_only_counter(client):
    sid = make_swap(client, *ORIG)
    r = client.post(f"/api/swaps/{sid}/counter", json={
        "a_day": COUNTER[0][0], "a_task": COUNTER[0][1],
        "b_day": COUNTER[1][0], "b_task": COUNTER[1][1]})
    assert r.status_code == 200, r.text
    body = r.json()["counter"]
    assert body["a_member"] == 1 and body["b_member"] == 2  # 反案冻结成员

    r = client.post(f"/api/swaps/{sid}/confirm", json={"proposal": "counter"})
    assert r.status_code == 200, r.text
    assert r.json()["selected"] == "counter"

    board = board_map(client)
    # 本周看板只反映所选（反）案交换结果
    assert board[COUNTER[0]] == 2 and board[COUNTER[1]] == 1
    # 原案那两格不动
    assert board[ORIG[0]] == 1 and board[ORIG[1]] == 2

    d = client.get(f"/api/swaps/{sid}").json()
    assert d["status"] == "confirmed" and d["selected"] == "counter"
    assert d["applied"] == {
        "a_day": 1, "a_task": 1, "b_day": 1, "b_task": 2,
        "a_member": 1, "b_member": 2,
        "a_member_name": "阿明", "b_member_name": "小雨"}
    # 原案四元组与成员快照保留可查
    assert d["original"] == {
        "a_day": 0, "a_task": 1, "b_day": 0, "b_task": 2,
        "a_member": 1, "b_member": 2,
        "a_member_name": "阿明", "b_member_name": "小雨"}


def test_confirm_original_applies_only_original(client):
    sid = make_swap(client, *ORIG)
    r = client.post(f"/api/swaps/{sid}/counter", json={
        "a_day": COUNTER[0][0], "a_task": COUNTER[0][1],
        "b_day": COUNTER[1][0], "b_task": COUNTER[1][1]})
    assert r.status_code == 200

    r = client.post(f"/api/swaps/{sid}/confirm", json={"proposal": "original"})
    assert r.status_code == 200, r.text
    assert r.json()["selected"] == "original"

    board = board_map(client)
    # 只反映原案
    assert board[ORIG[0]] == 2 and board[ORIG[1]] == 1
    assert board[COUNTER[0]] == 1 and board[COUNTER[1]] == 2

    d = client.get(f"/api/swaps/{sid}").json()
    assert d["selected"] == "original"
    assert (d["applied"]["a_day"], d["applied"]["a_task"]) == ORIG[0]
    # 反案仍保留可查
    assert d["counter"]["a_day"] == 1


def test_illegal_counter_leaves_pending_and_original_intact(client):
    before = board_map(client)
    sid = make_swap(client, *ORIG)

    r = client.post(f"/api/swaps/{sid}/counter", json={
        "a_day": ILLEGAL[0][0], "a_task": ILLEGAL[0][1],
        "b_day": ILLEGAL[1][0], "b_task": ILLEGAL[1][1]})
    assert r.status_code == 400
    assert r.json()["detail"] == "same_assignee"

    d = client.get(f"/api/swaps/{sid}").json()
    # 反案非法不改原 pending、不覆盖原案
    assert d["status"] == "pending"
    assert d["counter"] is None and d["selected"] is None
    assert (d["original"]["a_day"], d["original"]["a_task"]) == ORIG[0]
    assert board_map(client) == before

    # 原案依旧可确认
    r = client.post(f"/api/swaps/{sid}/confirm", json={"proposal": "original"})
    assert r.status_code == 200


def test_confirm_without_choice_fails_and_board_unchanged(client):
    before = board_map(client)
    sid = make_swap(client, *ORIG)

    r = client.post(f"/api/swaps/{sid}/confirm", json={})
    assert r.status_code == 400
    assert r.json()["detail"] == "proposal_required"

    # 格表不变、仍 pending
    assert board_map(client) == before
    d = client.get(f"/api/swaps/{sid}").json()
    assert d["status"] == "pending" and d["selected"] is None


def test_confirm_counter_without_counter_proposal_fails(client):
    before = board_map(client)
    sid = make_swap(client, *ORIG)

    r = client.post(f"/api/swaps/{sid}/confirm", json={"proposal": "counter"})
    assert r.status_code == 400
    assert r.json()["detail"] == "counter_missing"
    assert board_map(client) == before
