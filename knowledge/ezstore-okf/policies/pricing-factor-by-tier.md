---
type: Pricing Policy
title: 各客戶等級的報價因子區間
description: VIP 0.75–0.90、Standard 0.85–1.00、New 0.95–1.10，預設值與後端 DefaultPricingFactor 一致。
resource: http://localhost:8080/swagger/index.html
tags: [pricing, policy, customer-tier]
status: stable
generated:
  by: claude-opus-5.5/ezstore-okf
  at: 2026-10-18T22:30:00+08:00
policy_tiers:
  vip: {default: 0.80, min: 0.75, max: 0.90}
  standard: {default: 0.90, min: 0.85, max: 1.00}
  new: {default: 1.00, min: 0.95, max: 1.10}
---
# 規則

報價因子（pricing factor）乘上產品牌價就是單價，見 [總價](/metrics/total-price.md)。
建立報價單時，後端依 [客戶等級](/entities/customer-tier.md) 給預設值（`GET /api/v1/pricing-factor/{level}`）；業務可以調整，但必須落在下表區間內。

| 客戶等級 | 預設因子 | 允許區間 | 說明 |
|---|---|---|---|
| vip | 0.80 | 0.75 – 0.90 | 年度合約客戶，最多 75 折 |
| standard | 0.90 | 0.85 – 1.00 | 一般客戶 |
| new | 1.00 | 0.95 – 1.10 | 新客戶，原價為主，最多 95 折 |

# 超出區間時

- 低於下限：必須依 [核准層級](/policies/approval-matrix.md) 取得業務主管核准，並同時檢查 [利潤率下限](/policies/minimum-profit-rate.md)。
- 高於上限：不違法但有流失客戶的風險，建議調回上限並說明理由。
- 調整一律透過 [先複製再修改](/processes/copy-on-write-editing.md)，原報價單不動。

# Examples

- QT-20260330-001（魔女宅急便，new，因子 0.95）：在區間下限，合規。
- 把它改成 1.5：高於 new 的上限 1.10，建議調回 1.10。
- QT-20260115-001（史塔克工業，vip，因子 0.75）：在下限，但利潤率 28.4% 低於 30%，需主管核准。
