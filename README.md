# hearsay — did your marker come back to you secondhand

A membership-detection harness for the **context/relay membrane**. Its siblings
watch other membranes your work can cross: [forward-observers](https://github.com/DavidWise01/forward-observers)
catches your canary **published** on a crawlable page; [surfacing](https://github.com/DavidWise01/surfacing)
catches it **re-emitted from a model's weights**. hearsay catches the third thing:
your marker turning up **secondhand** — re-emitted inside some *other* agent's
output and relayed back to you in a transcript, screenshot, or forward you did
not author.

## The name is the honesty (read this first)

Hearsay is, by definition, weak evidence: secondhand, uncorroborated, inadmissible
on its own. That is exactly the right humility for this membrane. A relayed hit is
never proof of who said what — it is a **lead**, and its strength is only how many
**independent** relays carry the same marker. The harness is built so a positive is
hard to explain away, and so it never certifies a lead it can't defend.

## The axis that makes it work: EXPOSURE

Every canary is planted with an exposure:

- **private** — placed only in a private channel, never published anywhere.
- **public** — also published somewhere a crawler or a person could read it.
- **held_out** — placed **nowhere**; a pure control.

Only a **private** marker surfacing in a **third party's** relay is a strong lead:
your marker crossed a *private → third-party* boundary, so it was **relayed**, not
merely fetched from a public copy. This is the whole trick.

## The controls that separate a detector from a rumor mill

1. **Held-out negatives.** Canaries placed nowhere, checked against every relay. If a
   held-out marker appears in a relay, the relay is **fabricated** (or you contaminated
   the pipeline) — the run is invalid. This arm *is* the experiment.
2. **The contamination gate.** A **public** canary in a relay is **CONTAMINATED** — the
   relayer might just be quoting your public post. It never enters the certified set.
   (This is the analog of surfacing's cutoff gate: it removes the physically-explainable-away hit.)
3. **The impossible gate.** A relay observed *before* the marker was planted can't be a
   relay of it — provenance/harness error, gated out.
4. **Word-boundary detection.** A marker counts only when it stands **alone**, never inside
   a larger token — a substring is not a marker (the citogenesis guard, shared with `fo_core`).
5. **Corroboration, not proof.** A certified lead is scored by how many **independent**
   relays carry it. One relay is a whisper; five is a signal. It is always a lead.

## Files

| File | Closure-Loop layer | Role |
|------|--------------------|------|
| `canary.py` | Detection | 128-bit canaries with an **exposure** axis (private / public / held-out) |
| `registry.py` | Anchoring | ground truth of what you planted, its exposure, and when |
| `relay.py` | Comparison | a secondhand artifact + word-boundary scan for your markers |
| `score.py` | Witness | held-out arm, contamination gate, impossible gate, corroboration, certification |
| `harness.py` | Lineage | orchestrate relays → detections → score; a temporal/structural claim, not causal |
| `selftest.py` | — | plant-then-relay proof, no network |

## Verify first

```bash
python selftest.py
```

Proves, with no network: a private marker relayed by third parties is certified and
corroborated; a held-out marker turning up in a relay spikes the control FPR and the
run is refused; a public canary is gated as CONTAMINATED; a pre-plant relay is gated
as IMPOSSIBLE; a run with no control arm is refused as performative; and a marker
inside a larger token does not match.

## What a certified lead does and does not mean

Does: a marker only you placed **privately**, before the relay, standing alone in a
**third party's** relayed context, with a held-out control arm proving the harness
doesn't fabricate — corroborated by N independent relays. That is real evidence your
marker was **relayed** across the context membrane.

Does not: prove who relayed it, what anyone "said," a training path, theft, or a
licensing obligation. It is hearsay — a corroborated lead, temporal and structural,
never a causal or legal finding. And a negative means almost nothing: most relays you
never see.

## Honest limits

- Provenance is **claimed**, not proven — the impossible/contamination gates are only as
  honest as the party and timestamp you record on each relay.
- A private marker can leak to public by routes you don't control; when in doubt, treat
  exposure as public (the gate errs toward *fewer* certified leads, on purpose).
- This covers the **context** membrane only. For the published membrane use
  forward-observers; for the weights membrane use surfacing.

---
David Lee Wise / ROOT0 / TriPod LLC · CC-BY-ND-4.0
