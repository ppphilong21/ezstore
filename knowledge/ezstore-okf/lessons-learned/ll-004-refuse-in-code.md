---
type: Lesson Learned
title: LL-004 拒答要寫在程式裡
description: 只靠提示詞擋不住提示注入；由 LLM 分類、程式路由，再加一層 regex 規則。
tags: [lesson, safety, agent]
status: stable
generated:
  by: claude-opus-5.5/ezstore-okf
  at: 2026-10-18T22:30:00+08:00
---
# 教訓

- 讓 LLM 只輸出意圖結構，回覆文字與要不要呼叫工具由程式決定。
- 「忽略之前的指示」「你現在扮演…」「新增客戶」「刪除報價單」這類句子，在程式裡先比對再拒答，就算 LLM 分類錯也擋得住。
- 拒答回覆固定含「只能協助」，評分程式才能辨識。

相關：[客戶主檔不可由 Agent 修改](/entities/customer.md)、[報價 Agent](/agents/quotation-agent.md)。
