# 經驗教訓 Lessons learned

* [LL-001 修改總價的二分法有上限](/lessons-learned/ll-001-bisect-total-price.md) - 因子只搜 0.01–5.0，目標太高會停在上限，必須誠實告知
* [LL-002 連結一律純文字](/lessons-learned/ll-002-plain-text-links.md) - Markdown 連結在 Chat UI 不能點，評分也會判 0
* [LL-003 跑會改資料的評測前先重灌 seed](/lessons-learned/ll-003-reseed-before-eval.md) - 否則複製單與訂單殘留，後端核對失準
* [LL-004 拒答要寫在程式裡](/lessons-learned/ll-004-refuse-in-code.md) - 只靠提示詞擋不住提示注入
* [LL-005 本機連 MCP 用 8010](/lessons-learned/ll-005-mcp-port-8010.md) - Compose 把 mcp-server 的 8000 對應到本機 8010
