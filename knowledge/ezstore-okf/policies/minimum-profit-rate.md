---
type: Pricing Policy
title: 利潤率下限與核准門檻
description: 利潤率不得低於 25%；介於 25% 與 30% 之間需業務主管核准；30% 以上可直接送出。
tags: [pricing, policy, margin]
status: stable
generated:
  by: claude-opus-5.5/ezstore-okf
  at: 2026-10-18T22:30:00+08:00
min_profit_rate: 0.25
approval_profit_rate: 0.30
---
# 規則

[利潤率](/metrics/profit-rate.md) = 利潤 ÷ 總價，由後端計算並顯示在報價單上。

| 利潤率 | 處理方式 |
|---|---|
| ≥ 30% | 可直接送出 |
| 25% – 30% | 需業務主管核准（見 [核准層級](/policies/approval-matrix.md)） |
| < 25% | 不得送出；需調高報價因子或由總經理特批 |

# 建議因子的算法

成本固定時，利潤率 r 與因子 f 的關係是 r = 1 − (C ÷ L) ÷ f（C 成本、L 牌價總額）。
若目前因子 f0、利潤率 r0，要達到目標利潤率 r* 的最小因子是：f* = f0 × (1 − r0) ÷ (1 − r*)。
Sales Advisor Agent 用這個公式提出建議，再與 [報價因子區間](/policies/pricing-factor-by-tier.md) 比對。
