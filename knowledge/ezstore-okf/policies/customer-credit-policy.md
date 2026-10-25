---
type: Credit Policy
title: 客戶信用與轉訂單規則
description: 信用分數 50 以上可直接轉訂單；40–49 轉訂單需預付 30%；低於 40 需總經理核准後才能轉訂單。
resource: http://localhost:8080/api/v1/customers
tags: [policy, credit, order]
status: stable
generated:
  by: claude-opus-5.5/ezstore-okf
  at: 2026-10-18T22:30:00+08:00
credit_rules:
  - {below: 40, action: "需總經理核准後才能轉訂單"}
  - {below: 50, action: "轉訂單需預付 30% 訂金"}
---
# 規則

[客戶](/entities/customer.md) 的 `credit_score`（0–100）存在後端客戶主檔。轉訂單前依 [轉訂單檢核](/processes/order-conversion-checklist.md) 檢查：

| 信用分數 | 轉訂單條件 |
|---|---|
| ≥ 50 | 可直接轉訂單 |
| 40 – 49 | 需預付 30% 訂金 |
| < 40 | 需總經理核准（[核准層級](/policies/approval-matrix.md)） |

# Examples

- 魔女宅急便股份有限公司：new、信用 50 → 可直接轉訂單。
- 怪獸電力公司：new、信用 45 → 需預付 30%。
- 無臉男金融服務有限公司：new、信用 35 → 需總經理核准。
