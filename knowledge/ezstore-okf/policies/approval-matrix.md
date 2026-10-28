---
type: Approval Rule
title: 核准層級
description: 報價因子低於等級下限或利潤率低於 30% 需業務主管核准；利潤率低於 25% 或信用分數低於 40 需總經理核准。
tags: [policy, approval]
status: stable
generated:
  by: claude-opus-5.5/ezstore-okf
  at: 2026-10-18T22:30:00+08:00
---
# 核准矩陣

| 情境 | 核准人 | 依據 |
|---|---|---|
| 報價因子低於等級下限 | 業務主管 | [報價因子區間](/policies/pricing-factor-by-tier.md) |
| 利潤率 25% – 30% | 業務主管 | [利潤率下限](/policies/minimum-profit-rate.md) |
| 利潤率 < 25% | 總經理 | [利潤率下限](/policies/minimum-profit-rate.md) |
| 客戶信用分數 < 40 要轉訂單 | 總經理 | [信用規則](/policies/customer-credit-policy.md) |
| 修改已發佈（published）的報價單 | 不可修改，只能複製後改副本 | [報價單生命週期](/processes/quotation-lifecycle.md) |

AI Agent 不能代替人核准：Agent 只能指出需要誰核准，並產生副本或建議。
