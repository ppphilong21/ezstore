---
type: AI Agent
title: 報價 Agent quotation_agent
description: Graph Workflow，透過 MCP 操作報價單；以 A2A 對其他 Agent 開放六項技能。
resource: http://agent:8080/a2a/quotation_agent/.well-known/agent-card.json
tags: [agent, a2a, mcp]
status: stable
generated:
  by: claude-opus-5.5/ezstore-okf
  at: 2026-10-18T22:30:00+08:00
---
# 技能（A2A agent card）

查詢報價單、查詢客戶的報價單清單、複製報價單、修改報價因子、修改總價、報價單轉訂單。所有修改遵守 [先複製再修改](/processes/copy-on-write-editing.md)。

# 怎麼呼叫

A2A JSON-RPC `POST http://agent:8080/a2a/quotation_agent`，訊息用自然語言，例如「我要查詢報價單，報價單編號：QT-20260330-001」。回覆是純文字並附系統連結。
