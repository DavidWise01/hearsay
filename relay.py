#!/usr/bin/env python3
"""Relays = Detection + Comparison.

A RELAY is a piece of text you did NOT author that reaches you secondhand: a
screenshot of someone's chat with a model, a forwarded transcript, a pasted
answer. Each relay carries a claimed PROVENANCE (who produced it) and a
timestamp. Detection is the same word-boundary rule the whole family uses:
a canary counts only when it stands alone, never inside a larger token
(that is the citogenesis guard -- a substring match is not a marker).

  party of a relay:
    "third_party" : produced in someone else's context (the strong case).
    "public_index": produced by / lifted from a public crawlable source
                    (weak -- this is what forward-observers already covers).
    "self"        : produced in your own context (not evidence of anything).
"""
from __future__ import annotations
import re
from dataclasses import dataclass


def scan_text(text: str, values):
    """Return the canary values that stand ALONE in text (word-boundary).

    A value matches only when not flanked by [A-Za-z0-9_-], so `abc123` does
    NOT match inside `xabc123y`. Case-sensitive, exactly like fo_core.scan_text.
    """
    found = []
    for v in values:
        if not v:
            continue
        pat = r"(?<![A-Za-z0-9_-])" + re.escape(v) + r"(?![A-Za-z0-9_-])"
        if re.search(pat, text):
            found.append(v)
    return found


@dataclass
class Relay:
    text: str                 # the secondhand artifact's content
    party: str = "third_party"  # third_party | public_index | self
    observed_utc: str | None = None  # when the relay reached you
    source: str = ""          # human note on where it came from

    def canaries_in(self, values):
        return scan_text(self.text, values)
