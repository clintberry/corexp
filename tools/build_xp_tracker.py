"""Build XP_Tracker.html at the repo root from the badge markdown files.

Usage:  python3 tools/build_xp_tracker.py
Then print XP_Tracker.html to PDF (half-letter pages), e.g. with headless Chrome:
  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless --no-pdf-header-footer \
      --print-to-pdf=XP_Tracker.pdf XP_Tracker.html
"""
import html
import pathlib
import re
import subprocess
from urllib.parse import quote

ROOT = pathlib.Path(__file__).resolve().parent.parent

LEVELS = [("Explorer", "★☆☆"), ("Builder", "★★☆"), ("Master", "★★★")]
LEVEL_RE = re.compile(r"^## (Explorer|Builder|Master) \(Level \d\) · (\d+) XP")
REQ_RE = re.compile(r"^(\d+)\. (.*) — \*\*(\d+) XP\*\*$")
EPIC_RE = re.compile(r"^\| (★+) (\w+) \| (.*) \| \*\*(\d+) XP\*\* \|$")
RING_RE = re.compile(r'<circle cx="200" cy="200" r="172" fill="(#[0-9a-fA-F]{6})"')

CATEGORY_COLORS = {
    1: "#2b4c7e", 2: "#c8403a", 3: "#7b4ba8", 4: "#3b7dd8",
    5: "#2f8f4e", 6: "#1f8a9e", 7: "#b5652f",
}

esc = html.escape
MEDAL = "assets/winged-lion-medal-print.jpg"


def parse_badge(md_path):
    lines = md_path.read_text().splitlines()
    title = re.sub(r"^#\s+\S+\s+", "", lines[0]).strip()
    tagline = next((l.strip("* ") for l in lines[1:6] if l.startswith("**")), "")
    levels, epics, current = [], [], None
    for line in lines:
        m = LEVEL_RE.match(line)
        if m:
            current = {"name": m.group(1), "xp": int(m.group(2)), "reqs": []}
            levels.append(current)
            continue
        m = REQ_RE.match(line)
        if m and current:
            current["reqs"].append((m.group(1), m.group(2), int(m.group(3))))
            continue
        m = EPIC_RE.match(line)
        if m:
            epics.append((m.group(1), m.group(2), m.group(3), int(m.group(4))))
    assert len(levels) == 3 and len(epics) == 3, md_path
    for lv in levels:
        assert sum(x for *_, x in lv["reqs"]) == lv["xp"], f"{md_path}: {lv['name']} total mismatch"

    logo = md_path.parent / "logo.svg"
    ring = RING_RE.search(logo.read_text())
    return {
        "title": title,
        "tagline": tagline,
        "levels": levels,
        "epics": epics,
        "logo": quote(str(logo.relative_to(ROOT))),
        "color": ring.group(1) if ring else "#2b4c7e",
        "req_xp": sum(lv["xp"] for lv in levels),
        "epic_xp": sum(e[3] for e in epics),
    }


def load_categories():
    cats = []
    for cat_dir in sorted(p for p in ROOT.iterdir() if p.is_dir() and re.match(r"\d\. ", p.name)):
        num, name = cat_dir.name.split(". ", 1)
        badges = [parse_badge(md) for md in sorted(cat_dir.glob("badges/*/*.md"))]
        cats.append({"num": int(num), "name": name, "badges": badges, "color": CATEGORY_COLORS[int(num)]})
    return cats


def load_patch_rules(cats):
    """Mark each badge required or elective, from the table in CoreXP_Awards.md, and return the elective rule."""
    text = (ROOT / "CoreXP_Awards.md").read_text()
    lines = text.splitlines()
    start = lines.index("| Category | Required | Electives |") + 2
    listed = {}
    for line in lines[start:]:
        if not line.startswith("|"):
            break
        _, required, electives = [c.strip() for c in line.strip("|").split("|")]
        for names, req in ((required, True), (electives, False)):
            for name in names.split(", "):
                if name != "—":
                    listed[name] = req
    titles = {b["title"] for c in cats for b in c["badges"]}
    assert set(listed) == titles, f"CoreXP_Awards.md badge table mismatch: {set(listed) ^ titles}"
    for c in cats:
        for b in c["badges"]:
            b["required"] = listed[b["title"]]
    electives = int(re.search(r"\*\*(\d+) electives\*\*", text).group(1))
    m = re.search(r"at least \*\*(\d+)\*\* from ([^.,]+)", text)
    cat = next(c for c in cats if c["name"] == m.group(2).strip())
    return {"electives": electives, "min_from": {"cat": cat["num"], "n": int(m.group(1))}, "category": cat["name"]}


def blank_row_cells():
    return '<td class="date"></td><td class="init"></td>'


def badge_page(b, cat):
    rows = []
    for lv, (_, stars) in zip(b["levels"], LEVELS):
        rows.append(
            f'<tr class="lvl"><th colspan="3"><span class="stars">{stars}</span> {lv["name"]}</th>'
            f'<th class="xp">{lv["xp"]}</th><th class="date">Date</th><th class="init">Mentor</th></tr>'
        )
        for num, text, xp in lv["reqs"]:
            rows.append(
                f'<tr><td class="chk"></td><td class="num">{num}</td><td>{esc(text)}</td>'
                f'<td class="xp">{xp}</td>{blank_row_cells()}</tr>'
            )
    rows.append(
        '<tr class="lvl epic"><th colspan="3"><span class="stars">⚡</span> Epic Quests</th>'
        f'<th class="xp">{b["epic_xp"]}</th><th class="date">Date</th><th class="init">Mentor</th></tr>'
    )
    for stars, tier, text, xp in b["epics"]:
        rows.append(
            f'<tr><td class="chk"></td><td class="num tier">{stars}</td><td><b>{tier}:</b> {esc(text)}</td>'
            f'<td class="xp">{xp}</td>{blank_row_cells()}</tr>'
        )
    return f'''
<section class="sheet badge-page" style="--main:{b["color"]};--dark:{b["color"]}">
  <header class="badge-head">
    <img src="{b["logo"]}" alt="">
    <div>
      <div class="kicker">{cat["num"]}. {esc(cat["name"])}</div>
      <h2>{esc(b["title"])}</h2>
      <div class="tag">{esc(b["tagline"])}</div>
    </div>
    <div class="earned-box"><span>XP earned</span><b>____</b><em>of {b["req_xp"] + b["epic_xp"]}</em></div>
  </header>
  <table class="xplog">
    <colgroup><col class="c-chk"><col class="c-num"><col><col class="c-xp"><col class="c-date"><col class="c-init"></colgroup>
    {"".join(rows)}
  </table>
</section>'''


def category_page(cat):
    items = "".join(
        f'<li><img src="{b["logo"]}" alt=""><span>{esc(b["title"])}{tag(b)}</span>'
        f'<em>{b["req_xp"]} + {b["epic_xp"]} XP</em></li>'
        for b in cat["badges"]
    )
    total = sum(b["req_xp"] + b["epic_xp"] for b in cat["badges"])
    return f'''
<section class="sheet cat-page" style="--main:{cat["color"]};--dark:{cat["color"]}">
  <div class="cat-num">Category {cat["num"]}</div>
  <h1>{esc(cat["name"])}</h1>
  <p class="cat-total">{len(cat["badges"])} badges · {total} XP available</p>
  <ul class="cat-list">{items}</ul>
</section>'''


def tag(b):
    return "" if b["required"] else ' <span class="elective">Elective</span>'


def scoreboard(cats, rules):
    rows = []
    for cat in cats:
        rows.append(f'<tr class="cat" style="--main:{cat["color"]}"><th colspan="6">{cat["num"]}. {esc(cat["name"])}</th></tr>')
        for b in cat["badges"]:
            rows.append(
                f'<tr><td>{esc(b["title"])}{tag(b)}</td><td class="sq"></td><td class="sq"></td><td class="sq"></td>'
                f'<td class="sq"></td><td class="earned">/ {b["req_xp"] + b["epic_xp"]}</td></tr>'
            )
    grand = sum(b["req_xp"] + b["epic_xp"] for c in cats for b in c["badges"])
    return f'''
<section class="sheet scoreboard">
  <h2 class="page-title"><small>All badges at a glance</small>Scoreboard</h2>
  <p class="note">Check a box when a level is signed off. Write each badge's XP total as it grows. A level patch takes every required badge at that level plus {rules["electives"]} electives (at least {rules["min_from"]["n"]} from {esc(rules["category"])}).</p>
  <table class="score">
    <thead><tr><th>Badge</th><th>Exp</th><th>Bld</th><th>Mas</th><th>Epic</th><th>XP</th></tr></thead>
    {"".join(rows)}
    <tfoot><tr><th colspan="5">Grand total</th><th class="earned">/ {grand}</th></tr></tfoot>
  </table>
</section>'''


def make_print_medal():
    # Medal photo, shrunk for print (macOS sips) so the PDFs stay small.
    subprocess.run(["sips", "-Z", "1200", str(ROOT / "awards" / "winged-lion-medal.jpg"), "--out", str(ROOT / MEDAL)], check=True, capture_output=True)


def cover():
    # The four big awards: the Winged Lion medal on top, the three level patches below.
    patches = "".join(
        f'<img src="level-patches/{lvl.lower()}-poster.svg" alt="{lvl} patch">'
        for lvl, _ in LEVELS)
    return f'''
<section class="sheet cover">
  <div class="brand">CoreXP</div>
  <h1 style="margin-top:0.1in">XP Tracker</h1>
  <p class="tagline">Every badge. Every requirement. Every point.</p>
  <figure class="medal"><img src="{MEDAL}" alt=""><figcaption>Winged Lion Award</figcaption></figure>
  <div class="patches">{patches}</div>
  <div class="owner">
    <div class="field"><span>Name</span><span class="blank"></span></div>
    <div class="field"><span>Mentor</span><span class="blank"></span></div>
    <div class="cols">
      <div class="field"><span>Started</span><span class="blank"></span></div>
      <div class="field"><span>Age</span><span class="blank"></span></div>
    </div>
  </div>
</section>'''


GUIDE = '''
<section class="sheet">
  <h2 class="page-title"><small>How it works</small>Earning XP</h2>
  <div class="why">
    <p>Every badge requirement is worth XP. When you finish one, check its box, write the date, and have your mentor initial it. That XP is now yours.</p>
    <p>Each badge also has three optional <b>Epic Quests</b>: big stretch challenges you can earn once, any time.</p>
  </div>
  <h3>What requirements are worth</h3>
  <table class="tracker guide">
    <thead><tr><th>Size</th><th>XP</th><th>What it looks like</th></tr></thead>
    <tbody>
      <tr><th>Quick</th><td>2</td><td>One sitting: name, learn, talk about, or share something</td></tr>
      <tr><th>Task</th><td>5</td><td>Make, write, practice, or roleplay, or repeat a habit 2–5 days</td></tr>
      <tr><th>Project</th><td>10</td><td>Plan and complete, teach, lead, interview, present, or a ~1 week habit</td></tr>
      <tr><th>Challenge</th><td>20</td><td>A 2–4 week habit, or a major project or certification</td></tr>
      <tr><th>Marathon</th><td>40</td><td>A habit kept for 2+ months</td></tr>
    </tbody>
  </table>
  <h3 style="margin-top:14px">Epic Quest tiers</h3>
  <table class="tracker guide">
    <tbody>
      <tr><th>★ Challenger</th><td>15 XP</td></tr>
      <tr><th>★★ Champion</th><td>25 XP</td></tr>
      <tr><th>★★★ Legend</th><td>40 XP</td></tr>
    </tbody>
  </table>
  <h3 style="margin-top:14px">How to log it</h3>
  <ol class="how">
    <li>Use your badge booklet (if there is one) to record the work itself.</li>
    <li>On the badge's page here, check the box, write the date, and get mentor initials.</li>
    <li>When a whole level is done, check it off on the Scoreboard.</li>
    <li>Keep a running total in the "XP earned" box at the top of each badge page.</li>
  </ol>
</section>'''

STYLE = '''
  .cover h1 { font-size: 34pt; }
  .cover figure { margin: 0; }
  .cover figcaption { font-family: var(--display); font-weight: 600; text-transform: uppercase; letter-spacing: 0.12em; color: var(--main); }
  .cover .medal { margin-top: 0.18in; }
  .cover .medal img { display: block; margin: 0 auto; height: 3.35in; border-radius: 10px; border: 3px solid #b08a4a; box-shadow: 0 0 0 1.5px var(--ink); }
  .cover .medal figcaption { font-size: 11pt; margin-top: 6px; }
  .cover .patches { display: flex; justify-content: center; gap: 0.22in; margin: 0.16in 0 0.1in; }
  .cover .patches img { display: block; width: 1.3in; }

  .note { font-size: 8.5pt; color: var(--muted); }
  table.score { width: 100%; border-collapse: collapse; font-size: 7pt; line-height: 1.12; }
  table.score th, table.score td { border-bottom: 1px solid var(--rule); padding: 0.5px 4px; text-align: left; }
  table.score thead th { font-size: 7pt; text-transform: uppercase; letter-spacing: 0.05em; color: var(--muted); }
  table.score tr.cat th { background: var(--main); color: #fff; font-family: var(--display); font-weight: 600; font-size: 7.5pt; padding: 1px 6px; }
  table.score td.sq { width: 0.34in; }
  table.score td.sq::before { content: ''; display: inline-block; width: 9px; height: 9px; border: 1.2px solid var(--ink); border-radius: 2px; vertical-align: -1px; }
  table.score .earned { width: 0.65in; text-align: right; color: var(--muted); }
  table.score tfoot th { border-top: 2px solid var(--ink); font-family: var(--display); font-size: 10pt; padding-top: 4px; }

  .elective { font-family: 'Nunito', sans-serif; font-size: 0.75em; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; color: var(--muted); border: 1px solid var(--rule); border-radius: 3px; padding: 0 3px; margin-left: 3px; }

  table.guide td:nth-child(2) { font-weight: 700; width: 0.5in; }
  table.guide td:nth-child(3) { text-align: left; }

  .cat-page { display: flex; flex-direction: column; }
  .cat-page .cat-num { font-family: var(--display); font-weight: 600; letter-spacing: 0.18em; text-transform: uppercase; color: var(--main); font-size: 10pt; margin-top: 0.4in; }
  .cat-page h1 { font-size: 26pt; color: var(--main); margin: 4px 0; }
  .cat-page .cat-total { color: var(--muted); border-bottom: 3px solid var(--main); padding-bottom: 10px; }
  .cat-list { list-style: none; padding: 0; margin: 10px 0 0; }
  .cat-list li { display: flex; align-items: center; gap: 12px; padding: 4px 0; border-bottom: 1px dotted var(--rule); font-size: 11pt; font-weight: 700; }
  .cat-list img { width: 0.55in; }
  .cat-list em { margin-left: auto; font-style: normal; font-weight: 400; font-size: 9pt; color: var(--muted); }

  .badge-head { display: flex; align-items: center; gap: 10px; margin-bottom: 8px; }
  .badge-head img { width: 0.72in; flex: none; }
  .badge-head .kicker { font-size: 7pt; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; color: var(--muted); }
  .badge-head h2 { font-size: 16pt; color: var(--main); }
  .badge-head .tag { font-size: 8pt; font-style: italic; color: var(--muted); }

  table.xplog { width: 100%; border-collapse: collapse; font-size: 7.2pt; line-height: 1.18; }
  table.xplog col.c-chk { width: 0.17in; }
  table.xplog col.c-num { width: 0.2in; }
  table.xplog col.c-xp { width: 0.3in; }
  table.xplog col.c-date { width: 0.5in; }
  table.xplog col.c-init { width: 0.42in; }
  table.xplog td { border-bottom: 1px solid var(--rule); padding: 2px 3px; vertical-align: middle; }
  table.xplog td.date, table.xplog td.init { border-left: 1px solid var(--rule); }
  table.xplog td.num { color: var(--muted); text-align: center; }
  table.xplog td.tier { color: var(--main); font-size: 6.5pt; letter-spacing: -1px; }
  table.xplog td.xp { text-align: center; font-weight: 700; color: var(--main); }
  table.xplog td.chk::before { content: ''; display: block; width: 9px; height: 9px; border: 1.2px solid var(--ink); border-radius: 2px; }
  table.xplog tr.lvl th { background: var(--main); color: #fff; text-align: left; padding: 3px 5px; font-family: var(--display); font-weight: 600; font-size: 8.5pt; }
  table.xplog tr.lvl th.xp { text-align: center; }
  table.xplog tr.lvl th.date, table.xplog tr.lvl th.init { font-family: 'Nunito', sans-serif; font-size: 6.5pt; font-weight: 700; text-transform: uppercase; letter-spacing: 0.04em; text-align: center; }
  table.xplog tr.lvl .stars { color: #ffe08a; margin-right: 3px; }
  table.xplog tr.lvl.epic th { background: var(--ink); }
  table.xplog tr:not(.lvl) + tr.lvl th { border-top: 4px solid #fff; }

  .badge-head > div:nth-child(2) { flex: 1; }
  .earned-box { flex: none; text-align: center; border: 2px solid var(--main); border-radius: 10px; padding: 4px 8px; line-height: 1.1; }
  .earned-box span { display: block; font-size: 6pt; font-weight: 700; text-transform: uppercase; letter-spacing: 0.06em; color: var(--muted); }
  .earned-box b { display: block; font-family: var(--display); font-size: 13pt; color: var(--main); }
  .earned-box em { font-style: normal; font-size: 7pt; color: var(--muted); }
'''


def build():
    make_print_medal()
    cats = load_categories()
    rules = load_patch_rules(cats)
    parts = [cover(), GUIDE, scoreboard(cats, rules)]
    for cat in cats:
        parts.append(category_page(cat))
        parts.extend(badge_page(b, cat) for b in cat["badges"])
    doc = f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>CoreXP XP Tracker</title>
  <!-- Generated by tools/build_xp_tracker.py from the badge markdown files. Edit those, then rebuild. -->
  <link rel="stylesheet" href="assets/booklet.css">
  <style>{STYLE}</style>
</head>
<body>
<div class="print-tip">
  <strong>Printing tip:</strong> Pages are half-letter (5.5″ × 8.5″). Print to PDF, then print that PDF as a booklet (or 2 pages per sheet) and fold.
</div>
{"".join(parts)}
</body>
</html>
'''
    out = ROOT / "XP_Tracker.html"
    out.write_text(doc)
    n = sum(len(c["badges"]) for c in cats)
    print(f"Wrote {out.name}: {len(cats)} categories, {n} badges")


if __name__ == "__main__":
    build()
