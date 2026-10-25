---
type: Business Entity
title: 訂單 Order
description: 由報價單轉換或直接建立，編號 ORD-YYYYMMDD-NNN，可關聯原報價單。
resource: http://localhost:8080/api/v1/orders
tags: [entity, order]
status: stable
generated:
  by: claude-opus-5.5/ezstore-okf
  at: 2026-10-18T22:30:00+08:00
---
# Schema

| 欄位 | 說明 |
|---|---|
| `order_number` | ORD-YYYYMMDD-NNN |
| `customer_id` | FK 到 [客戶](/entities/customer.md) |
| `quotation_id` | 來源 [報價單](/entities/quotation.md)，可為空（急單直接下訂） |
| `total_price` | 品項小計加總 |
| `status` | pending、confirmed、completed、cancelled |

轉換規則見 [轉訂單檢核](/processes/order-conversion-checklist.md)。轉訂單不會改動原報價單，也不會把它發佈。
