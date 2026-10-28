---
type: Business Entity
title: 產品 Product
description: 產品主檔，含成本與牌價；報價單品項保存建立當下的成本與牌價快照。
resource: http://localhost:8080/api/v1/products
tags: [entity, product]
status: stable
generated:
  by: claude-opus-5.5/ezstore-okf
  at: 2026-10-18T22:30:00+08:00
---
# Schema

| 欄位 | 說明 |
|---|---|
| `product_number` | EQ-001 這類料號 |
| `cost` | 成本，用於 [利潤率](/metrics/profit-rate.md) |
| `list_price` | 牌價，用於 [總價](/metrics/total-price.md) |
| `inventory` | 庫存 |

報價單品項是快照：產品改價不會影響已建立的 [報價單](/entities/quotation.md)，但複製報價單時會重新抓最新牌價。
