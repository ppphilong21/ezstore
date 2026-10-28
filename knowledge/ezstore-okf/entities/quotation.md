---
type: Business Entity
title: 報價單 Quotation
description: 報價單主檔與品項，編號 QT-YYYYMMDD-NNN，草稿可改、發佈後不可改。
resource: http://localhost:8080/api/v1/quotations
tags: [entity, quotation]
status: stable
generated:
  by: claude-opus-5.5/ezstore-okf
  at: 2026-10-18T22:30:00+08:00
---
# Schema

| 欄位 | 型別 | 說明 |
|---|---|---|
| `quotation_number` | string | QT-YYYYMMDD-NNN，當日流水號，唯一 |
| `customer_id` | int | FK 到 [客戶](/entities/customer.md) |
| `customer_level` | string | 建立時的 [客戶等級](/entities/customer-tier.md) 快照 |
| `pricing_factor` | decimal(5,4) | [報價因子](/policies/pricing-factor-by-tier.md) |
| `total_price` | decimal(14,2) | [總價](/metrics/total-price.md) |
| `profit_amount` / `profit_rate` | decimal | [利潤率](/metrics/profit-rate.md) |
| `status` | string | draft 或 published，見 [生命週期](/processes/quotation-lifecycle.md) |
| `notes` | text | 複製時會寫「複製自 QT-…」 |
| `items[]` | list | 品項快照：產品名稱、成本、牌價、單價、數量、小計，見 [產品](/entities/product.md) |

系統頁面：http://localhost:3000/quotations/{id}。精確查詢：`GET /api/v1/quotations?quotation_number=QT-20260330-001`。
