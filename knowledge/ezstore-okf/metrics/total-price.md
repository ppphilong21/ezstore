---
type: Metric
title: 總價 Total Price
description: 單價 = 牌價 × 報價因子，總價 = Σ 單價 × 數量；調整總價時以二分法反推報價因子。
tags: [metric, pricing]
status: stable
generated:
  by: claude-opus-5.5/ezstore-okf
  at: 2026-10-18T22:30:00+08:00
---
# Computation

- `unit_price = list_price × pricing_factor`
- `subtotal = unit_price × quantity`
- `total_price = Σ subtotal`

# Examples

QT-20260330-001：A4影印紙牌價 650 × 0.95 = 617.5，× 10 箱 = 6175。因子改 1.5 → 9750。

修改總價時 MCP 工具用二分法在因子 0.01–5.0 之間找最接近的值（最多 20 次），所以目標總價最多約為牌價總額的 5 倍，見 [二分法經驗](/lessons-learned/ll-001-bisect-total-price.md)。
