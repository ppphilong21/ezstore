---
type: Lesson Learned
title: LL-003 跑會改資料的評測前先重灌 seed
description: 否則複製單與訂單殘留，後端核對失準。
tags: [lesson, eval, data]
status: stable
generated:
  by: claude-opus-5.5/ezstore-okf
  at: 2026-10-18T22:30:00+08:00
---
# 教訓

`quotation-actions.json` 每跑一次就會新增 3 張副本與 1 張訂單；第二次跑時「至少 3 張副本」「訂單關聯」等核對會混到上一次的資料。

```bash
docker compose exec db psql -U ezstore -f /scripts/seed-test-data.sql
```

grade_agent.py 對 actions 群組會自動重灌；手動跑 `agents-cli eval run` 時要自己重灌。

相關：[先複製再修改](/processes/copy-on-write-editing.md)、[訂單](/entities/order.md)。
