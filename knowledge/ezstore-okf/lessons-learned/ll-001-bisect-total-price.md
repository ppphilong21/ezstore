---
type: Lesson Learned
title: LL-001 修改總價的二分法有上限
description: 因子只搜 0.01–5.0，目標太高會停在上限，必須誠實告知。
tags: [lesson, pricing, mcp]
status: stable
generated:
  by: claude-opus-5.5/ezstore-okf
  at: 2026-10-18T22:30:00+08:00
sources:
  - id: mcp
    resource: https://github.com/cshliu77/ezstore/blob/workshop-start/mcp_server/server.py
    title: MCP Server adjust_total_price
---
# 發生什麼

把 QT-20260330-001（牌價總額 6500）的總價改成 100000，工具迭代 20 次後停在因子 5.0、總價 32500[^mcp]。

# 教訓

- 可達範圍是牌價總額 × [0.01, 5.0]；超出時回覆必須說「已達最大迭代次數」並附實際總價，不可宣稱成功。
- 二分法會建立一張副本（[先複製再修改](/processes/copy-on-write-editing.md)），失敗也留下一張草稿。
- 評分規則要接受「誠實說明做不到」，見 [總價](/metrics/total-price.md)。

[^mcp]: mcp_server/server.py, BISECT_LOW/BISECT_HIGH = 0.01/5.0, BISECT_MAX_ITERATIONS = 20
