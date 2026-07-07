#!/usr/bin/env python3
"""Scoring + controls. The held-out control arm, the contamination gate, and
the impossible-time gate do the epistemic work; without them a relayed hit
means nothing.

A DETECTION is one (canary, relay) pair where the canary stands ALONE in the
relay text. Each detection is tiered:

  HARD         : a PRIVATE canary in a THIRD-PARTY relay, observed after it was
                 planted -> your marker crossed a private->third-party boundary,
                 so it was relayed, not fetched. A strong LEAD (still hearsay).
  CONTAMINATED : a PUBLIC canary in a third-party relay -> the relayer could just
                 be quoting your public copy. Gated out of the certified set.
  PUBLISHED    : a relay whose party is a public index -> that is the PUBLISHED
                 membrane (forward-observers' job), not the context membrane.
  IMPOSSIBLE   : relay observed BEFORE the canary was planted -> provenance/
                 harness error, not a relay.
  SELF         : found in your own context -> not evidence of anything.
  CONTROL      : a HELD-OUT canary in any relay -> fabrication/contamination ->
                 the run is invalid (the harness is manufacturing hearsay).

Certification rule: a run certifies HARD leads only if a held-out control arm
was actually run and its false-positive rate is 0. Otherwise INVALID. And a
certified HARD lead is always a LEAD needing corroboration -- never proof of
who relayed it. Corroboration = the number of INDEPENDENT third-party relays
carrying the same canary.
"""
from __future__ import annotations
from canary import HEX_LEN


def _before(a, b):
    if not a or not b:
        return False
    return a[:19] < b[:19]


def tier(d):
    if d["held_out"]:
        return "CONTROL"
    if d["party"] == "self":
        return "SELF"
    if d["party"] == "public_index":
        return "PUBLISHED"
    if _before(d["observed_utc"], d["planted_utc"]):
        return "IMPOSSIBLE"
    if d["exposure"] == "public":
        return "CONTAMINATED"
    if d["exposure"] == "private":
        return "HARD"
    return "OTHER"


def score(detections, registry_entries):
    held_total = [e for e in registry_entries if e["held_out"]]
    n_held = len(held_total)

    for d in detections:
        d["tier"] = tier(d)

    control_hits = {d["value"] for d in detections if d["tier"] == "CONTROL"}
    fpr = (len(control_hits) / n_held) if n_held else None

    # HARD leads, grouped by canary, with corroboration = distinct relays
    hard = {}
    for d in detections:
        if d["tier"] == "HARD":
            hard.setdefault(d["value"], set()).add(d.get("relay_id", id(d)))
    contaminated = {d["value"] for d in detections if d["tier"] == "CONTAMINATED"}
    impossible = {d["value"] for d in detections if d["tier"] == "IMPOSSIBLE"}

    # base rate: chance a 128-bit token appears by accident across all checks
    checks = max(1, len(detections))
    base_rate = checks * (2 ** -(HEX_LEN * 4))

    if n_held == 0:
        verdict = "INVALID: no held-out control arm was run (performative)"
        certified = {}
    elif fpr and fpr > 0:
        verdict = (f"INVALID: control FPR={fpr:.2f} -- the harness is manufacturing "
                   f"hearsay (fabricated/contaminated relay); no lead is trustworthy")
        certified = {}
    else:
        certified = hard
        verdict = (f"CLEAN: control FPR=0 over {n_held} held-out; "
                   f"{len(certified)} corroborated lead(s) -- hearsay, needs corroboration")

    return {
        "verdict": verdict,
        "certified_leads": {v: len(relays) for v, relays in certified.items()},
        "hard": {v: len(relays) for v, relays in hard.items()},
        "contaminated": sorted(contaminated),
        "impossible": sorted(impossible),
        "control_hits": sorted(control_hits),
        "control_fpr": fpr,
        "held_out_n": n_held,
        "base_rate": base_rate,
    }
