---
type: Process
title: 先複製再修改 Copy-on-write
description: 修改報價因子或總價時，系統先複製報價單再改副本，原報價單永遠不動，回覆會標示「未修改」。
resource: https://github.com/cshliu77/ezstore/blob/workshop-start/mcp_server/server.py
tags: [process, quotation, audit]
status: stable
generated:
  by: claude-opus-5.5/ezstore-okf
  at: 2026-10-18T22:30:00+08:00
---
# 步驟

1. 依編號找到原 [報價單](/entities/quotation.md)。
2. `POST /quotations/{id}/duplicate` 建立草稿副本（備註「複製自 QT-…」）。
3. 在副本上 `PUT` 新的報價因子（或以二分法逼近目標總價）。
4. 回覆原單（未修改）與新單的系統連結。

# 為什麼

- 已發佈的報價單不能改（見 [生命週期](/processes/quotation-lifecycle.md)），複製是唯一合法路徑。
- 保留稽核軌跡：客戶看過的版本不會被悄悄改掉。
