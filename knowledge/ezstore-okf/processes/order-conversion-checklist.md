---
type: Playbook
title: 轉訂單檢核
description: 轉訂單前確認報價因子在區間內、利潤率合規、客戶信用條件、品項數量與核准紀錄。
tags: [process, order, checklist]
status: stable
generated:
  by: claude-opus-5.5/ezstore-okf
  at: 2026-10-18T22:30:00+08:00
---
# 檢核清單

1. 報價因子在 [等級區間](/policies/pricing-factor-by-tier.md) 內，或已有主管核准。
2. [利潤率](/policies/minimum-profit-rate.md) ≥ 25%；介於 25%–30% 需主管核准。
3. 客戶 [信用條件](/policies/customer-credit-policy.md)：< 50 預付 30%，< 40 總經理核准。
4. 品項與數量與客戶確認過的版本一致（轉換時用報價單的單價建立訂單品項）。
5. 依 [核准層級](/policies/approval-matrix.md) 完成核准後，才請報價 Agent 轉訂單。

轉訂單由 [報價 Agent](/agents/quotation-agent.md) 的 convert_to_order 執行，訂單會關聯原報價單。
