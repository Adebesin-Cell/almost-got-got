#!/usr/bin/env python3
"""Regenerate the survey charts in index.html from the raw Google Forms CSV.

Usage: python3 scripts/build_charts.py "<path to responses.csv>"

Rewrites everything between the CHARTS:START / CHARTS:END markers in index.html,
so the figures on the site are always derived from the CSV rather than typed by hand.
"""
import csv, sys, html, collections, pathlib, re

CSV = sys.argv[1] if len(sys.argv) > 1 else None
ROOT = pathlib.Path(__file__).resolve().parent.parent
INDEX = ROOT / "index.html"

Q_TYPE, Q_END, Q_LOC = "What kind of scam was it?", "How did it end?", "Where are you?"
GOT, ALMOST, SPOT = "They got me", "Almost — but I caught it in time", "I spotted it right away"
OUTCOMES = [GOT, ALMOST, SPOT]
OUT_SHORT = {GOT: "Got them", ALMOST: "Caught it in time", SPOT: "Spotted it at once"}

# Buckets that carry no analytical meaning: kept visible, never used to draw a conclusion.
UNCLASSIFIED = {"Something else", "Not sure", ""}

SHORT = {
    'OTP or PIN theft ("just read me the code")': "OTP / PIN theft",
    "Someone pretending to be tech support / an official": "Fake tech support",
    "WhatsApp or social account takeover": "Account takeover",
    "Phishing link (email, SMS, DM)": "Phishing link",
    "Fake scholarship, job, or grant offer": "Fake scholarship / job",
    "Fake login page": "Fake login page",
    'Fake payment / "I paid you twice" refund': "Fake-payment refund",
    "Romance or marketplace scam": "Romance / marketplace",
    "Deepfake voice note / AI-cloned voice": "Deepfake voice",
    'A "found" USB / flash drive': '"Found" USB drive',
    "Someone following you into a building": "Tailgating",
    "Free-wifi or QR-code trap": "Free-wifi / QR trap",
    "Something else": "Something else",
    "Not sure": "Not sure",
}
def short(t): return SHORT.get(t, t or "No answer")


def load(path):
    with open(path, newline="", encoding="utf-8") as fh:
        return [r for r in csv.DictReader(fh)]


def e(s): return html.escape(str(s), quote=True)


def bar_chart(rows, total):
    """Chart A - nominal categories, magnitude. One hue for every bar (never a
    value-ramp on nominal categories); unclassified buckets in the muted tone."""
    top = max(c for _, c in rows)
    out = ['<figure class="viz" role="group" aria-labelledby="vizA-t">',
           '<figcaption class="viz-cap"><h3 id="vizA-t">What kind of scam was it?</h3>',
           f'<p class="viz-sub">All {total} responses, one answer each. Bars share a single colour, length is the only comparison.</p></figcaption>',
           '<div class="hbars">']
    for label, count in rows:
        pct = count / total * 100
        muted = " is-muted" if label in UNCLASSIFIED else ""
        tip = f"{short(label)} — {count} of {total} responses ({pct:.0f}%)"
        out.append(
            f'<div class="hbar{muted}" tabindex="0" data-tip="{e(tip)}">'
            f'<span class="hb-l">{e(short(label))}</span>'
            f'<span class="hb-track"><span class="hb-fill" style="width:{count/top*100:.2f}%"></span></span>'
            f'<span class="hb-v">{count}</span></div>')
    out.append('</div><p class="viz-note">The two muted rows at the bottom are catch-all options, not findings. '
               '"Something else" is the single largest single answer at 23 of 100, which caps how much weight the '
               'ranking above it can carry: a fifth of respondents did not see their scam in our list.</p>')
    out.append('</figure>')
    return "\n".join(out)


def diverging(title, sub, rows, note=None, tid="vizB"):
    """Chart B - ordered-scale share, so a diverging stacked bar centred on the
    neutral middle category. Left of centre = the scam worked, right = it did not.
    CVD dE for the pole pair sits in the 6-8 band, so direct labels + 2px surface
    gaps carry identity alongside hue."""
    out = [f'<figure class="viz" role="group" aria-labelledby="{tid}-t">',
           f'<figcaption class="viz-cap"><h3 id="{tid}-t">{e(title)}</h3><p class="viz-sub">{sub}</p></figcaption>',
           '<div class="dv-legend">']
    for k, cls in ((GOT, "got"), (ALMOST, "almost"), (SPOT, "spot")):
        out.append(f'<span class="dv-key"><i class="sw {cls}"></i>{e(OUT_SHORT[k])}</span>')
    out.append('</div><div class="dvrows">')
    for label, counts, n in rows:
        g, a, s = (counts.get(k, 0) for k in OUTCOMES)
        gp, ap, sp = (v / n * 100 for v in (g, a, s))
        muted = " is-muted" if label in UNCLASSIFIED else ""
        segs_l = [("almost", ap / 2, a), ("got", gp, g)]      # row-reverse: centre outward
        segs_r = [("almost", ap / 2, a), ("spot", sp, s)]
        def seg(cls, w, cnt, whole):
            if w <= 0: return ""
            tip = f"{short(label)} — {OUT_SHORT[dict(got=GOT, almost=ALMOST, spot=SPOT)[cls]]}: {cnt} of {n} ({whole:.0f}%)"
            return f'<span class="dv-seg {cls}" style="flex-basis:{w:.3f}%" tabindex="0" data-tip="{e(tip)}"></span>'
        out.append(
            f'<div class="dvrow{muted}">'
            f'<span class="dv-l">{e(short(label))} <em>n={n}</em></span>'
            f'<span class="dv-plot">'
            f'<span class="dv-end left">{gp:.0f}%</span>'
            f'<span class="dv-half l">{"".join(seg(c, w, k, gp if c=="got" else ap) for c, w, k in segs_l)}</span>'
            f'<span class="dv-half r">{"".join(seg(c, w, k, sp if c=="spot" else ap) for c, w, k in segs_r)}</span>'
            f'<span class="dv-end right">{sp:.0f}%</span>'
            f'</span></div>')
    out.append('</div>')
    if note: out.append(f'<p class="viz-note">{note}</p>')
    out.append('</figure>')
    return "\n".join(out)


def table(types, total):
    h = ['<details class="viz-table"><summary>View the figures as a table</summary>',
         '<div class="t-scroll">',
         '<table><caption>Scam type by outcome, all responses</caption><thead><tr><th scope="col">Scam type</th>']
    for k in OUTCOMES: h.append(f'<th scope="col">{e(OUT_SHORT[k])}</th>')
    h.append('<th scope="col">No answer</th><th scope="col">Total</th></tr></thead><tbody>')
    for label, counts, n in types:
        h.append(f'<tr><th scope="row">{e(short(label))}</th>')
        for k in OUTCOMES: h.append(f'<td>{counts.get(k,0)}</td>')
        h.append(f'<td>{counts.get("",0)}</td><td>{n}</td></tr>')
    h.append(f'</tbody></table></div><p class="viz-note">n={total} responses.</p></details>')
    return "\n".join(h)


def main():
    if not CSV: sys.exit("pass the responses CSV path")
    rows = load(CSV)
    total = len(rows)

    tcount = collections.Counter(r[Q_TYPE].strip() for r in rows)
    by_type = collections.defaultdict(collections.Counter)
    for r in rows:
        by_type[r[Q_TYPE].strip()][r[Q_END].strip()] += 1
    overall = collections.Counter(r[Q_END].strip() for r in rows)
    answered = sum(overall[k] for k in OUTCOMES)

    # Chart A: every type, biggest first, with the catch-all buckets pinned to the
    # bottom so they never interrupt the ranking they cannot contribute to.
    a_rows = sorted(tcount.items(), key=lambda kv: (kv[0] in UNCLASSIFIED, -kv[1], short(kv[0])))

    # Chart B: types with n>=4 ranked by how often the scam worked; the small tail
    # folded into one honest "Other" row; catch-all buckets pinned to the bottom.
    big = [(t, by_type[t], tcount[t]) for t in tcount if tcount[t] >= 4 and t not in UNCLASSIFIED]
    big.sort(key=lambda x: -(x[1].get(GOT, 0) / x[2]))
    tail = [t for t in tcount if tcount[t] < 4 and t not in UNCLASSIFIED]
    if tail:
        c = collections.Counter()
        for t in tail: c.update(by_type[t])
        big.append((f"Other ({len(tail)} types)", c, sum(tcount[t] for t in tail)))
    for t in tcount:
        if t in UNCLASSIFIED: big.append((t, by_type[t], tcount[t]))

    parts = [
        '<!-- CHARTS:START  generated by scripts/build_charts.py, do not hand-edit -->',
        diverging("How it ended, overall",
                  f'Every response that answered, n={answered}. Left of the centre line the scam worked; right of it, it did not.',
                  [("All responses", overall, answered)], tid="vizC"),
        bar_chart(a_rows, total),
        diverging("Which scams actually work",
                  "Share of each scam type by outcome, ranked by how often it succeeded. "
                  "Only types with four or more reports are ranked.",
                  big,
                  note="Read the ranking, not the individual bars: at these sample sizes a single response moves a row several points. "
                       "The pattern worth keeping is the spread between the top and bottom rows, not the exact percentages.",
                  tid="vizB"),
        table([(t, by_type[t], tcount[t]) for t, _ in a_rows], total),
        '<!-- CHARTS:END -->',
    ]
    block = "\n".join(parts)

    src = INDEX.read_text(encoding="utf-8")
    new, n = re.subn(r"<!-- CHARTS:START.*?<!-- CHARTS:END -->", block, src, flags=re.S)
    if not n: sys.exit("markers not found in index.html")
    INDEX.write_text(new, encoding="utf-8")
    print(f"charts rebuilt from {total} responses (outcome n={answered})")


if __name__ == "__main__":
    main()
