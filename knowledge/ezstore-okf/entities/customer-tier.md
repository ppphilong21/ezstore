---
type: Business Concept
title: 客戶等級 Customer Tier
description: vip、standard、new 三級，決定預設報價因子與允許的折扣區間。
resource: http://localhost:8080/api/v1/pricing-factor/vip
tags: [entity, customer, pricing]
status: stable
generated:
  by: claude-opus-5.5/ezstore-okf
  at: 2026-10-18T22:30:00+08:00
---
# 定義

| 等級 | 意義 | 預設因子 |
|---|---|---|
| vip | 年度合約或高信用客戶 | 0.80 |
| standard | 一般往來客戶 | 0.90 |
| new | 首次往來不滿一年 | 1.00 |

允許區間見 [報價因子區間](/policies/pricing-factor-by-tier.md)。報價單會保存建立當下的等級快照（`customer_level`）。
