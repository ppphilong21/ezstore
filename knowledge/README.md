# EZStore knowledge (OKF)

`ezstore-okf/` is an [Open Knowledge Format](https://github.com/GoogleCloudPlatform/knowledge-catalog/tree/main/okf)
(OKF v0.2) bundle: a folder of markdown files with YAML frontmatter, one concept per file, linked with plain
markdown links. The concept ID is the path without `.md` (e.g. `policies/minimum-profit-rate`).

| Folder | Concepts |
|---|---|
| `policies/` | pricing-factor ranges per tier, minimum profit rate, approval matrix, credit rules (machine-readable keys in frontmatter) |
| `entities/` | quotation, order, customer, customer tier, product |
| `metrics/` | total price, profit rate |
| `processes/` | copy-on-write editing, quotation lifecycle, order-conversion checklist |
| `lessons-learned/` | five lessons from building and evaluating the EZStore agent |
| `agents/` | the quotation agent (A2A card) and the sales advisor |

Every directory has an `index.md` (progressive disclosure) and the root has `log.md` (change history, newest first).
The sales advisor agent (`../advisor_agent`) reads this bundle at runtime. Validate and visualise it:

```bash
cd advisor_agent && uv run python scripts/okf_validate.py && uv run python scripts/okf_graph.py -o okf-graph.html
```

Concepts carry `generated: claude-opus-5.5/ezstore-okf`. After you review a concept, add
`verified: {by: "human:<your-id>", at: <ISO datetime>}` so readers know a person checked it.
