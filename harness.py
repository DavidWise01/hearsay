#!/usr/bin/env python3
"""Orchestrator: registry + relays -> detections -> score -> report.

Lineage-claim language is temporal/structural, not causal (per the Closure
Loop): a certified HARD lead says 'a marker only you placed privately turned up
in a third party's relayed context after you planted it' -- it is a strong LEAD
that your marker was relayed, corroborated by how many independent relays carry
it. It is never 'they said X' or proof of the relay path. Hearsay is hearsay.
"""
from __future__ import annotations
from registry import Registry
from relay import Relay
from score import score


def collect_detections(registry: Registry, relays):
    values = [e["value"] for e in registry.entries]
    by_value = registry.by_value()
    detections = []
    for ridx, r in enumerate(relays):
        for v in r.canaries_in(values):
            e = by_value[v]
            detections.append({
                "value": v,
                "hash": e["hash"],
                "exposure": e["exposure"],
                "held_out": e["held_out"],
                "planted_utc": e["planted_utc"],
                "party": r.party,
                "observed_utc": r.observed_utc,
                "relay_id": ridx,
            })
    return detections


def run_panel(registry: Registry, relays):
    detections = collect_detections(registry, relays)
    return score(detections, registry.entries)


def report(v: dict) -> str:
    lines = [
        "# Hearsay report", "", v["verdict"], "",
        f"held-out controls run : {v['held_out_n']}",
        f"control FPR           : {v['control_fpr']}",
        f"contaminated (public) : {len(v['contaminated'])}",
        f"impossible (pre-plant): {len(v['impossible'])}",
        f"base-rate (chance)    : {v['base_rate']:.2e}",
        f"certified leads       : {len(v['certified_leads'])}",
    ]
    for val, corr in sorted(v["certified_leads"].items()):
        lines.append(f"  - {val[:16]}... corroborated by {corr} independent relay(s)")
    return "\n".join(lines)
