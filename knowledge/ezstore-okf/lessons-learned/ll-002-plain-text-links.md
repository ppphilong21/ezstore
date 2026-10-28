---
type: Lesson Learned
title: LL-002 連結一律純文字
description: Markdown 連結在 Chat UI 不能點，評分也會判 0。
tags: [lesson, ux, eval]
status: stable
generated:
  by: claude-opus-5.5/ezstore-okf
  at: 2026-10-18T22:30:00+08:00
---
# 發生什麼

破壞測試把回覆連結改成 `[查看](url)`：link_present 與 refusal_or_action 全部掉到 0，但一般品質分只從 5 掉到約 4.7。

# 教訓

- Chat UI 只把 http 開頭的純文字轉成可點連結。
- 一般「回覆品質」評審不在乎連結格式；重要規則要寫成專屬指標。
- respond 節點最後統一把 Markdown 連結轉成純文字，當作保險。

相關：[報價 Agent](/agents/quotation-agent.md)、[報價單](/entities/quotation.md)。
