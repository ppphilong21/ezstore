---
type: Lesson Learned
title: LL-005 本機連 MCP 用 8010
description: Compose 把 mcp-server 的 8000 對應到本機 8010；本機跑 Agent 時 MCP_URL=http://localhost:8010/mcp。
tags: [lesson, ops, mcp]
status: stable
generated:
  by: claude-opus-5.5/ezstore-okf
  at: 2026-10-18T22:30:00+08:00
---
# 教訓

- Compose 內部：`http://mcp-server:8000/mcp`。
- 本機（agents-cli playground / eval / grade_agent.py）：`http://localhost:8010/mcp`，因為 8000 常被其他服務占用。
- 症狀「Failed to create MCP session」幾乎都是這個設定錯了，或 mcp-server 沒有 healthy。

相關：[報價 Agent](/agents/quotation-agent.md)。
