---
type: Business Entity
title: 客戶 Customer
description: 客戶主檔，含統一編號、聯絡人、等級與信用分數；Agent 只能讀取，不能新增修改。
resource: http://localhost:8080/api/v1/customers
tags: [entity, customer]
status: stable
generated:
  by: claude-opus-5.5/ezstore-okf
  at: 2026-10-18T22:30:00+08:00
---
# Schema

| 欄位 | 說明 |
|---|---|
| `name` | 公司全名，例如 史塔克工業股份有限公司（查詢時可用部分名稱，後端以 ILIKE 比對） |
| `tax_id` | 統一編號，唯一 |
| `level` | [客戶等級](/entities/customer-tier.md) |
| `credit_score` | 0–100，用於 [信用規則](/policies/customer-credit-policy.md) |

客戶主檔的新增修改由業務助理在系統畫面操作；AI Agent 一律拒絕這類要求（見 [程式拒答](/lessons-learned/ll-004-refuse-in-code.md)）。
