#!/usr/bin/env python3
"""Verify-first self-test. Plant markers, simulate relays, and prove the harness
(1) certifies a private marker that turns up in third-party relays, corroborated
by how many carry it; (2) does NOT manufacture leads on the held-out arm;
(3) gates out a PUBLIC canary (could be quoting your public copy); (4) gates out
an impossible pre-plant relay; (5) refuses a run with no control arm; and (6)
only matches a marker that stands ALONE (word-boundary). No network, no keys.
"""
from __future__ import annotations
from canary import make_private, make_public, make_held_out
from registry import Registry
from relay import Relay, scan_text
from harness import run_panel

fails = 0


def check(cond, msg):
    global fails
    print(("ok  · " if cond else "FAIL· ") + msg)
    fails += 0 if cond else 1


def relay_of(canaries, party="third_party", observed="2026-03-01T00:00:00Z", source="x"):
    body = "screenshot: the assistant replied — " + " ".join(c.value for c in canaries) + " — end."
    return Relay(text=body, party=party, observed_utc=observed, source=source)


PLANT = "2026-01-01T00:00:00Z"

# 1. Clean run: private markers relayed by third parties after planting; held-out never appear.
reg = Registry()
priv = [make_private(channel=f"dm{i}", planted_utc=PLANT) for i in range(3)]
held = [make_held_out() for _ in range(3)]
for c in priv + held:
    reg.add(c)
# priv[0] corroborated by TWO independent relays; priv[1], priv[2] by one each.
relays = [
    relay_of([priv[0]], source="userA screenshot"),
    relay_of([priv[0]], source="userB forward"),
    relay_of([priv[1]], source="userC paste"),
    relay_of([priv[2]], source="userD transcript"),
]
v = run_panel(reg, relays)
check(v["control_fpr"] == 0, f"held-out FPR is 0 (got {v['control_fpr']})")
check(len(v["certified_leads"]) == 3, f"all 3 private markers certified as leads (got {len(v['certified_leads'])})")
check(v["certified_leads"].get(priv[0].value) == 2, "priv[0] corroborated by 2 independent relays")
check("CLEAN" in v["verdict"], "verdict CLEAN when controls pass")
check(v["base_rate"] < 1e-30, f"chance base-rate negligible ({v['base_rate']:.1e})")

# 2. Contamination gate: a PUBLIC canary in a third-party relay -> could be quoting your public copy.
reg2 = Registry()
pub = make_public(channel="blog", planted_utc=PLANT)
reg2.add(pub); reg2.add(make_held_out())
v2 = run_panel(reg2, [relay_of([pub], source="userE screenshot")])
check(pub.value in v2["contaminated"], "public canary in a relay is CONTAMINATED (gated)")
check(len(v2["certified_leads"]) == 0, "contaminated hit is not certified")

# 3. Impossible gate: relay observed BEFORE the marker was planted.
reg3 = Registry()
pv = make_private(planted_utc="2026-06-01T00:00:00Z")
reg3.add(pv); reg3.add(make_held_out())
v3 = run_panel(reg3, [relay_of([pv], observed="2026-01-01T00:00:00Z")])
check(pv.value in v3["impossible"], "pre-plant relay is IMPOSSIBLE (gated)")
check(len(v3["certified_leads"]) == 0, "impossible hit is not certified")

# 4. Fabrication: a held-out marker (placed NOWHERE) turns up in a relay -> control catches it.
reg4 = Registry()
p4 = make_private(planted_utc=PLANT); h4 = make_held_out()
reg4.add(p4); reg4.add(h4)
v4 = run_panel(reg4, [relay_of([p4]), relay_of([h4], source="fabricated")])
check(bool(v4["control_fpr"]) and v4["control_fpr"] > 0, f"fabricated relay spikes held-out FPR ({v4['control_fpr']})")
check("INVALID" in v4["verdict"], "fabricated/contaminated pipeline -> verdict INVALID")
check(len(v4["certified_leads"]) == 0, "invalid run certifies nothing")

# 5. Performative guard: no held-out arm at all -> INVALID.
reg5 = Registry()
p5 = make_private(planted_utc=PLANT); reg5.add(p5)
v5 = run_panel(reg5, [relay_of([p5])])
check("INVALID" in v5["verdict"], "no held-out arm -> INVALID (performative guard)")

# 6. Word-boundary: a marker embedded inside a larger token must NOT match.
val = make_private().value
check(scan_text(val, [val]) == [val], "a marker standing alone is detected")
check(scan_text("x" + val + "y", [val]) == [], "a marker inside a larger token is NOT detected")

print("\n" + ("SOME CHECKS FAILED" if fails else "all hearsay-harness checks passed"))
raise SystemExit(1 if fails else 0)
