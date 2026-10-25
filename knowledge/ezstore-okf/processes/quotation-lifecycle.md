---
type: Process
title: 報價單生命週期
description: 草稿（draft）可修改與刪除；發佈（published）後不可修改、不可刪除；任一狀態都可以轉訂單。
tags: [process, quotation]
status: stable
generated:
  by: claude-opus-5.5/ezstore-okf
  at: 2026-10-18T22:30:00+08:00
---
# 狀態

```
draft ──publish──▶ published
  │                    │
  └──── convert ───────┴──▶ order（原報價單狀態不變）
```

- draft：可修改、可刪除、可發佈。
- published：修改回 403、刪除回 403、再發佈回 400。要調價只能 [先複製再修改](/processes/copy-on-write-editing.md)。
- 轉訂單見 [轉訂單檢核](/processes/order-conversion-checklist.md)。
