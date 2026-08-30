# laserbrain-grimdall

A project that runs on the laserbrain infrastructure, with that infrastructure vendored
here so it can be read and worked against directly rather than only through a package
manager.

## The layout

Every directory here is a plain duplicate of one repository, named after it.

| directory | duplicate of |
|---|---|
| `laserbrain/` | [degibug-del/laserbrain](https://github.com/degibug-del/laserbrain) — the base repo: SDK, hooks, MCP server, the grammar, the plugin |
| `laserbrain-corpus/` | [degibug-del/laserbrain-corpus](https://github.com/degibug-del/laserbrain-corpus) — the measurement corpus and the studies that read it |

That is the whole rule. A directory name tells you which repository it came from, and
nothing here needs a table to decode.

```bash
./refresh-vendor.sh          # re-copy both from ~/laserbrain and ~/laserbrain-corpus
```

The script verifies each copy equals its upstream's tracked files exactly, because the same
refresh done by hand elsewhere leaked build artifacts twice and silently dropped two files
for nine days.

## What changed on 2026-08-30

This was three git subtrees named `sdk/`, `lasermind/` and `lasergear/`. Two problems.

The names had stopped matching the repositories: `lasermind` and `lasergear` were renamed to
`laserbrain-corpus` and `laserbrain-instructions`, so the directory names pointed at nothing
and a provenance table was doing the work a name should do.

And the content had converged. `lasergear`'s hooks live in `laserbrain` and ship inside the
wheel, so the tree carried the same three hook modules twice under two names — and they
diverged, one copy falling 146 lines behind with a live gate bug the whole time. `sdk/` was
the laserbrain repo, which is now `laserbrain/`.

The corpus is the one thing `laserbrain` deliberately does not carry, so it stays as its own
duplicate. A repository that holds its own measurements can be tuned until they agree with
it; keeping them apart is what makes the algorithms worth re-running.

## Where the truth lives

- **grammar.json** is the single source. Copies exist across the surfaces and a build gate
  fails if any two disagree.
- **drift-vectors.json** is generated *from* the Python implementation, so Python is the
  reference and the JS and TS implementations are checked against it, never the reverse.
- Anything under `laserbrain-corpus/` described as a corpus is **one machine and one agent**.

`degibug-del/laserbrain-sdk` is deliberately absent. It was a second copy of the SDK that sat
at 0.53.0 while the published one moved on, and fifteen build scripts read the stale one for
five days before anyone noticed. It was retired on 2026-08-24 and archived on 2026-08-30.
Bringing it in would rebuild the problem retiring it solved.
