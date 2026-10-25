---
type: AI Agent
title: 業務顧問 Agent sales_advisor
description: 讀這份 OKF 知識檢查報價政策，透過 A2A 請報價 Agent 執行操作。
resource: http://localhost:8502/dev-ui/?app=sales_advisor
tags: [agent, a2a, okf]
status: stable
generated:
  by: claude-opus-5.5/ezstore-okf
  at: 2026-10-18T22:30:00+08:00
---
# 做什麼

- 回答政策問題，並引用概念 ID（例如 policies/minimum-profit-rate）。
- 檢查一張報價單是否合規：透過 A2A 向 [報價 Agent](/agents/quotation-agent.md) 取得報價單，讀 [報價因子區間](/policies/pricing-factor-by-tier.md)、[利潤率下限](/policies/minimum-profit-rate.md)、[信用規則](/policies/customer-credit-policy.md)，給出結論與建議因子。
- 使用者確認後，透過 A2A 請報價 Agent 修改報價因子（產生副本）。
