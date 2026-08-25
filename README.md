# laserbrain-grimdall

**laserbrain is a goal-alignment harness that asserts an agent's grammatical goal as it is
first stated, and stops the agent before the next tool call when that goal moves due to
agentic context-drift.** The goal is frozen where the agent cannot revise it; a turn of yours
re-grounds it, and a declared parent goal licenses a sub-task — neither is drift.

This repo is laserbrain in one tree: the SDK, the corpus that calibrates it, and the gate that
enforces coverage. Each subtree keeps the full history of the repo it came from, so
`git log` still reaches the reasoning behind any line.

| path         | from                     | what it is                                                   |
|--------------|--------------------------|--------------------------------------------------------------|
| `sdk/`       | `degibug-del/laserbrain` | the published package — python, javascript, typescript, json |
| `lasermind/` | `degibug-del/lasermind`  | the corpus, the attention calibration, the local MCP server   |
| `lasergear/` | `degibug-del/lasergear`  | the coverage gate and the hooks                               |

`degibug-del/laserbrain-sdk` is deliberately **not** here. It was a second copy of the
SDK that sat at 0.53.0 while the published one moved to 0.55.0, and fifteen build
scripts read the stale one for five days before anyone noticed. It was retired on
2026-08-24. Bringing it in would rebuild the problem retiring it solved.

## Where the truth lives

- **grammar.json** is the single source. Five copies exist across the surfaces and a
  build gate fails if any two disagree.
- **drift-vectors.json** is generated *from* the Python implementation, so Python is the
  reference and the JS and TS implementations are checked against it — never the other
  way round.
- Anything under `lasermind/` described as a corpus is **one machine and one agent**.
  `attention.json` records `dominant_agent_share: 1.0`, and its own provenance block
  says it calibrates this setup and is not a constant of anything. Treat every number
  derived from it as a fact about one operator until a second one contributes.

## Running the checks

```
cd sdk/python && for t in test_*.py; do python3 "$t"; done   # 44 suites
node sdk/javascript/test/parity.mjs                          # JS against Python
cd sdk/typescript && npx tsx test/parity.mjs                 # TS against Python
```

All three must agree on the vectors. If they disagree, the Python result is the one to
trust and the other two are wrong.
