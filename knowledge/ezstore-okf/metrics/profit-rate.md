---
type: Metric
title: 利潤率 Profit Rate
description: 利潤率 = (總價 − 總成本) ÷ 總價；政策下限 25%，低於 30% 需主管核准。
tags: [metric, margin]
status: stable
generated:
  by: claude-opus-5.5/ezstore-okf
  at: 2026-10-18T22:30:00+08:00
---
# Computation

- `profit_amount = Σ (unit_price − product_cost) × quantity`
- `profit_rate = profit_amount ÷ total_price`（總價為 0 時為 0）

# Examples

QT-20260330-001：成本 380 × 10 = 3800，總價 6175 → 利潤 2375，利潤率 0.3846。

政策門檻見 [利潤率下限與核准門檻](/policies/minimum-profit-rate.md)。
