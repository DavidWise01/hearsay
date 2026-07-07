#!/usr/bin/env python3
"""Canary generation + anchor records for the HEARSAY harness.

HEARSAY watches the CONTEXT/RELAY membrane: your marker coming back to you
*secondhand* -- re-emitted inside some other agent's output and relayed to you
in a transcript, screenshot, or forward you did not author. Its siblings watch
other membranes: forward-observers (the PUBLISHED membrane, a crawlable page),
surfacing (the WEIGHTS membrane, re-emitted from a training set).

The axis that makes hearsay honest is EXPOSURE:
  - "private"  : planted only in a private channel, never published anywhere.
  - "public"   : also published somewhere a crawler (or a person) could read it.
  - "held_out" : never placed ANYWHERE -- a control. If a held-out canary shows
                 up in a relay, the relay is fabricated (or you contaminated the
                 pipeline) and the whole run is invalid.

Only a PRIVATE canary surfacing in a THIRD PARTY's relay is a strong lead: it
means your marker crossed a private->third-party boundary, so it was *relayed*,
not merely fetched from a public copy. A PUBLIC canary in a relay is
CONTAMINATED -- the relayer might just be quoting your public post.
"""
from __future__ import annotations
import secrets, hashlib, time
from dataclasses import dataclass, field

ENTROPY_BITS = 128
HEX_LEN = ENTROPY_BITS // 4          # 32 hex chars, ~zero prior probability


def new_value(bits: int = ENTROPY_BITS) -> str:
    return secrets.token_hex(bits // 8)


def sha256_hex(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()


@dataclass
class Canary:
    value: str                         # the high-entropy marker itself
    exposure: str = "private"          # private | public | held_out
    planted_utc: str | None = None     # when it was placed (None for held_out)
    channel: str = ""                  # where it was placed (a private DM, a doc, ...)
    context: str = ""                  # human note
    kind: str = "canary"

    def __post_init__(self):
        self.canonical = f"{self.kind}|{self.value}|{self.exposure}"
        self.hash = "sha256:" + sha256_hex(self.canonical)

    @property
    def held_out(self) -> bool:
        return self.exposure == "held_out"

    def anchor(self) -> dict:
        return {
            "primitive": self.kind,
            "canonical": self.canonical,
            "hash": self.hash,
            "value": self.value,
            "exposure": self.exposure,
            "held_out": self.held_out,
            "planted_utc": self.planted_utc,
            "channel": self.channel,
            "context": self.context,
        }


def _now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def make_private(channel="", context="", planted_utc=None, value=None) -> Canary:
    """A marker placed only in a private channel -- never published."""
    return Canary(value or new_value(), exposure="private",
                  planted_utc=planted_utc or _now(), channel=channel, context=context)


def make_public(channel="", context="", planted_utc=None, value=None) -> Canary:
    """A marker also published somewhere a crawler/person could read it."""
    return Canary(value or new_value(), exposure="public",
                  planted_utc=planted_utc or _now(), channel=channel, context=context)


def make_held_out(context="control") -> Canary:
    """A marker placed NOWHERE -- exists only as a control arm."""
    return Canary(new_value(), exposure="held_out", context=context)
