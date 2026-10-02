# Chorerota · 家庭值日轮转

底座：成员+任务 → round-robin 生成周表 → 申请对调 → （可提反案）→ 显式选案确认改表。

反提案：pending 对调可由对方提交一套新四元组作反案（重过合法性、冻结反案双方成员，原案快照保留）；确认必须显式选 `original`/`counter`，未选案确认失败且格表不变。模块：`app/modules/swap_counter/`（反案校验 · 确认分派 · 详情双案投影）。

| 服务 | 端口 |
| --- | --- |
| 前端 | 5100 |
| API | 10100 |

```bash
docker compose up --build
pytest backend/app/tests
```

种子含 clean/dirty。0-1 空桩：`streak_badge` / `skip_week` / `chore_photo`。
