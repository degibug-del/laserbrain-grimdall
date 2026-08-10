# The blind probe — pre-registration

**Written 2026-08-10, before any result was read.** Every number below was chosen while the
answer was unknown, which is the only condition under which choosing them is free. Values
marked *proposed* are Diego's to change — but they must be changed **now**, not after a
first look. A threshold moved once the data is visible is fitted to it.

Implemented in `lb_gate.py`: `blind_arm`, `publish_blind_arm`.

---

## The question

Every session in the corpus to date ran with the harness visible. There has never been an
arm in which the instrument measured without also intervening, so *"does it help?"* has
been asserted and never answered. Diego's own read on 2026-08-07 was "yes, noticeably
better" — which is exactly the kind of belief that needs a control rather than a
testimonial.

**Does seeing the verdict change the work?**

## Design

| | |
|---|---|
| **unit** | one segment — the work between two `reset_task` calls, i.e. one task under one frozen ground |
| **assignment** | `sha256('blind:' + unit) % 2` — deterministic, 50/50, not re-rollable |
| **gate** | `LASERBRAIN_BLIND_PROBE=1`; otherwise every unit is sighted and nothing is running |
| **treatment** | the agent is told its reading |
| **control** | the reading is withheld: `{blind: true, …}`, work continues |
| **excluded** | anything with `LASERBRAIN_ARM=open` — that is a test harness, not a session |

The two arms differ **only in whether the agent is told.** The checks happen either way, Φ
is computed either way, and both are recorded either way. That is what makes the arms
comparable, and it is why the harness is not simply switched off for the control: a control
that recorded less Φ would be a different measurement, not a comparison.

## The record

Each assignment appends one line to `~/.claude/laserbrain/blind-arms.jsonl`:
`{session, unit, segment, blind, at}`.

**This did not exist until 2026-08-10.** The probe ran from 08-08 writing only
`current-arm.json`, which is overwritten per unit — so the first two days produced no
separable record and are excluded. The sample starts at the first line of that file.

## The outcome measure

**Primary: drift rate per unit** — the fraction of that unit's checks with
`drifting: true`, read from the session records in `~/.claude/laserbrain/*.json`, joined to
an arm through `blind-arms.jsonl`.

This is the right measure precisely because Φ is computed identically in both arms. The
control agent is not told it is drifting; the drift is still recorded. So the comparison
asks the question directly: **when an agent is told, does it drift less?**

**Secondary, reported but not decisive: catches per unit** — errors something independent
found (failed commands, logged by the hook). A treatment that reduces measured drift while
leaving real errors untouched would be moving the number rather than the work, and that is
worth being able to see.

## Sample and stopping rule

- **20 units per arm** (*proposed* — matches the sibling `probe_arm` pre-registration).
- **Stop when both arms reach 20.** Not when one does; not at a round date; not when the
  gap looks convincing.
- **No interim looks.** The first read of the outcome happens at n=20/20 and not before.
  This is the clause the whole document exists for: an experiment that can be stopped when
  the numbers please is measuring patience.
- If the probe is disabled or the design changes before n=20/20, the run is void and the
  file is restarted. A partial run is not a small result; it is no result.

## What would mean it does not help

Stated concretely, in advance, so it is recognisable if it happens:

> **The harness does not help if the sighted arm's mean drift rate is not lower than the
> blind arm's** — a difference of zero, or in the wrong direction, at n=20/20.

Any of these is that outcome and none of them is to be explained away:

- sighted ≥ blind on mean drift rate;
- a difference smaller than **0.05** (*proposed*) in drift rate — present but too small to
  justify a per-step instrument;
- a drift-rate difference with no matching movement in catches, which would say the reading
  changes what gets *recorded* rather than what gets *done*.

## What this cannot settle

**n=20 per arm is underpowered for a small effect.** It can detect a large difference and
will not resolve a subtle one, and no amount of running past 20 fixes that after the fact —
extending the sample once the result is visible is the same fault as moving a threshold.

The unit is one person's tasks on one machine. It measures whether *this* agent, doing
*this* work, drifts less when told. It is not a claim about agents in general, and the
write-up should not make one.

Both arms are the same agent, aware the probe exists. An agent that knows it is sometimes
blinded is not a naive control, and nothing here removes that.

---

*If any value above is wrong, change it before the first read. After that, it is the record
of what was decided when the answer was still unknown — which is all a pre-registration
ever is.*
