"""Build School_Year_Packet.html at the repo root: a printable monthly packet for school-year CoreXP Daily.

Usage:  python3 tools/build_monthly_packet.py
Then print to PDF (half-letter pages), e.g.:
  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless --no-pdf-header-footer \
      --print-to-pdf=School_Year_Packet.pdf School_Year_Packet.html
"""
import pathlib
import subprocess
from urllib.parse import quote

from build_xp_tracker import load_categories

ROOT = pathlib.Path(__file__).resolve().parent.parent
PATCH = "assets/winged-lion-patch-print.jpg"

DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
WEEKDAYS, MON_SAT, ALL, SAT = set(range(5)), set(range(6)), set(range(7)), {5}

# (quest, XP, days it applies). Edit here to retune the system.
QUESTS = [
    ("Homework", 3, WEEKDAYS),
    ("Spiritual goal", 1, ALL),
    ("Physical goal", 1, MON_SAT),
    ("Mental goal", 1, MON_SAT),
    ("Social goal", 1, ALL),
    ("Daily chore", 1, WEEKDAYS),
    ("Weekend chore", 3, SAT),
    ("Reading · 20 min", 1, MON_SAT),
    ("Music · 15 min", 1, WEEKDAYS),
]

GOALS = [
    ("Spiritual", "Scripture or devotional · Prayer · Gratitude journal"),
    ("Physical", "10 push-ups · Walk or bike 15 min · Stretch & drink water"),
    ("Mental", "Practice a skill 10 min · Flashcards · Learn one new thing"),
    ("Social", "Serve a sibling · Text or call someone · Act of kindness"),
]

def day_xp(d):
    return sum(xp for _, xp, days in QUESTS if d in days)


WEEK_XP = sum(day_xp(d) for d in range(7))
MONTH_XP = WEEK_XP * 4


def awards():
    # The Winged Lion patch on top, the three level patches below.
    patches = "".join(f'<img src="level-patches/{lvl}-poster.svg" alt="{lvl.title()} patch">' for lvl in ("explorer", "builder", "master"))
    return f'''<div class="awards">
    <figure><img class="top-patch" src="{PATCH}" alt=""><figcaption>Winged Lion Award</figcaption></figure>
    <div class="patches">{patches}</div>
  </div>'''


def cover():
    rows = "".join(
        f'<tr><th>{q}</th><td>{"Mon–Fri" if days == WEEKDAYS else "Mon–Sat" if days == MON_SAT else "Every day" if days == ALL else "Saturday"}</td><td class="xp">{xp}</td></tr>'
        for q, xp, days in QUESTS
    )
    return f'''
<section class="sheet cover">
  <div class="brand">CoreXP Daily · School Year</div>
  <h1 style="margin-top:0.12in">Monthly Quest Packet</h1>
  <p class="tagline">Do your part every day. Stack your XP all year.</p>
  {awards()}
  <div class="owner" style="margin-top:0.15in">
    <div class="cols">
      <div class="field"><span>Name</span><span class="blank"></span></div>
      <div class="field"><span>Month</span><span class="blank"></span></div>
    </div>
  </div>
  <h3 style="margin:14px 0 4px;align-self:flex-start">Daily Quests at a glance</h3>
  <table class="tracker glance">
    <thead><tr><th>Quest</th><th>When</th><th>XP</th></tr></thead>
    <tbody>{rows}
      <tr><th>Book report</th><td>Once a month</td><td class="xp">10</td></tr>
      <tr><th>Song performance</th><td>Once a month</td><td class="xp">10</td></tr>
    </tbody>
  </table>
  <p class="fine">A full school day earns <b>{day_xp(0)} XP</b>, Saturday <b>{day_xp(5)} XP</b>, Sunday <b>{day_xp(6)} XP</b>, for <b>{WEEK_XP} XP</b> a week. Badge XP is logged separately in your XP Tracker.
  No homework today? Do 20 minutes of study, review, or a learning app instead.</p>
</section>'''


def badge_menu_page():
    blocks = "".join(
        f'<div class="bm-cat" style="--main:{c["color"]}"><h4>{c["num"]}. {c["name"]}</h4>'
        + "".join(f'<div class="bm-badge"><img src="{b["logo"]}" alt=""><span>{b["title"]}</span></div>' for b in c["badges"])
        + "</div>"
        for c in load_categories()
    )
    return f'''
<section class="sheet">
  <h2 class="page-title"><small>Pick your next adventure</small>The Badge Menu</h2>
  <div class="why">
    <p>Badges earn their own XP. Work on any badge requirement whenever you like, and when it's
    signed off, log its XP in your <b>XP Tracker</b>. Pick one as your badge focus for the month.</p>
  </div>
  <div class="bm-grid">{blocks}</div>
</section>'''


def goals_page():
    goal_rows = "".join(
        f'<div class="goal"><div class="goal-cat">{cat}</div><div class="goal-body"><div class="blank"></div><div class="ideas">Ideas: {ideas}</div></div></div>'
        for cat, ideas in GOALS
    )
    return f'''
<section class="sheet">
  <h2 class="page-title"><small>Set these on the 1st</small>My Goals This Month</h2>
  <span class="label">My four daily goals</span>
  <p class="fine" style="margin-top:0">Small and steady beats big and skipped. Pick something you can do even on a busy school day.</p>
  {goal_rows}

  <div class="req" style="margin-top:12px">
    <div class="req-head"><div class="req-num">★</div><div class="req-title">Badge focus<span class="hint">Pick the badges you'll work on this month.</span></div></div>
    <div class="cols" style="grid-template-columns:2fr 1fr">
      <div class="field"><span>Badge</span><span class="blank"></span></div>
      <div class="field"><span>Level</span><span class="blank"></span></div>
    </div>
    <div class="cols" style="grid-template-columns:2fr 1fr">
      <div class="field"><span>Badge</span><span class="blank"></span></div>
      <div class="field"><span>Level</span><span class="blank"></span></div>
    </div>
    <div class="cols" style="grid-template-columns:2fr 1fr">
      <div class="field"><span>Badge</span><span class="blank"></span></div>
      <div class="field"><span>Level</span><span class="blank"></span></div>
    </div>
    <div class="field"><span>Epic Quest I'm chasing (optional)</span><span class="blank"></span></div>
  </div>

  <div class="req">
    <div class="req-head"><div class="req-num">+</div><div class="req-title">Monthly bonuses</div></div>
    <div class="field"><span>Book report on</span><span class="blank"></span></div>
    <div class="field"><span>Song I'll perform</span><span class="blank"></span></div>
  </div>

  <div class="cols">
    <div class="field"><span>My XP goal</span><span class="blank"></span></div>
    <div class="field"><span>Reward</span><span class="blank"></span></div>
  </div>
  <p class="fine">Most a month can earn: {MONTH_XP} XP from daily quests, plus monthly bonuses. Badge XP is tracked in your XP Tracker.</p>
</section>'''


def week_page(n):
    head = "".join(f"<th>{d}</th>" for d in DAYS)
    rows = []
    for q, xp, days in QUESTS:
        cells = "".join('<td></td>' if d in days else '<td class="off"></td>' for d in range(7))
        rows.append(f'<tr><th>{q}<span class="pts">{xp}</span></th>{cells}</tr>')
    totals = "".join(f'<td><span class="of">/{day_xp(d)}</span></td>' for d in range(7))
    rows.append(f'<tr class="total"><th>Day XP</th>{totals}</tr>')
    return f'''
<section class="sheet">
  <div class="week-head">
    <div><div class="kicker">Week {n}</div><h2>Quest Chart</h2></div>
    <div class="field"><span>Week of</span><span class="blank" style="width:1.1in;flex:none"></span></div>
  </div>
  <table class="week">
    <colgroup><col class="c-quest">{"<col>" * 7}</colgroup>
    <thead><tr><th></th>{head}</tr></thead>
    <tbody>{"".join(rows)}</tbody>
  </table>
  <p class="fine">Check each quest you finish. Gray boxes are days off.</p>

  <span class="label">Win of the week</span>
  <div class="lines" style="--n:1"></div>
  <span class="label">Badge progress this week (badge &amp; requirement)</span>
  <div class="lines" style="--n:2"></div>
  <div class="week-total">
    <div class="field"><span><b>Week total</b></span><span class="blank"></span></div>
    <div class="field"><span>Parent</span><span class="blank"></span></div>
  </div>
</section>'''


def wrapup():
    weeks = "".join(f'<tr><th>Week {n}</th><td></td></tr>' for n in range(1, 5))
    return f'''
<section class="sheet">
  <h2 class="page-title"><small>End of the month</small>Monthly Wrap-Up</h2>
  <table class="tracker log wrap">
    <tbody>
      {weeks}
      <tr><th>Book report (+10)</th><td></td></tr>
      <tr><th>Song performance (+10)</th><td></td></tr>
      <tr class="sum"><th>Month total</th><td></td></tr>
    </tbody>
  </table>
  <div class="checks" style="margin-top:8px"><span class="check">I hit my XP goal</span><span class="check">Badge focus done</span></div>
  <p class="fine">Signed off a badge requirement or Epic Quest? Log it in your <b>XP Tracker</b> too.</p>

  <span class="label">Which daily goal was easiest? Which was hardest?</span>
  <div class="lines" style="--n:2"></div>
  <span class="label">What am I most proud of this month?</span>
  <div class="lines" style="--n:2"></div>
  <span class="label">One thing I'll change next month</span>
  <div class="lines" style="--n:2"></div>

  <div class="level-done" style="margin-top:12px">
    <h3>★ Month Complete!</h3>
    <div class="cols">
      <div class="field"><span>Parent</span><span class="blank"></span></div>
      <div class="field"><span>Reward earned</span><span class="blank"></span></div>
    </div>
  </div>
</section>'''


STYLE = '''
  :root { --main: #2b4c7e; --dark: #1a2f52; --accent: #f2c14e; --tint: #ebf0f8; }
  .cover h1 { font-size: 26pt; }
  .awards { margin-top: 0.14in; display: flex; flex-direction: column; align-items: center; }
  .awards figure { margin: 0; text-align: center; }
  .awards .top-patch { display: block; margin: 0 auto; width: 1.5in; height: 1.5in; border-radius: 50%; }
  .awards figcaption { font-family: var(--display); font-weight: 600; font-size: 8.5pt; text-transform: uppercase; letter-spacing: 0.12em; color: var(--main); margin-top: 3px; }
  .awards .patches { display: flex; gap: 0.18in; margin-top: 0.08in; }
  .awards .patches img { width: 0.72in; }
  .fine { font-size: 8pt; color: var(--muted); margin-top: 6px; }

  table.glance th, table.glance td { padding-top: 2px; padding-bottom: 2px; height: 0.2in; }
  table.glance td { text-align: left; }
  table.glance td.xp { text-align: center; font-weight: 700; color: var(--main); width: 0.45in; }
  table.glance tbody th { width: 1.4in; }

  .bm-grid { columns: 2; column-gap: 14px; }
  .bm-cat { break-inside: avoid; margin-bottom: 7px; }
  .bm-cat h4 { font-family: var(--display); font-weight: 600; font-size: 8pt; color: #fff; background: var(--main);
    border-radius: 4px; padding: 2px 6px; margin: 0 0 2px; }
  .bm-badge { display: flex; align-items: center; gap: 6px; font-size: 7.8pt; padding: 1px 0; }
  .bm-badge img { width: 0.27in; }
  .pts { font-size: 7.5pt; font-weight: 700; color: var(--main); margin-left: 4px; }

  .goal { display: flex; align-items: stretch; border: 1.5px solid var(--rule); border-radius: 10px; margin-top: 7px; overflow: hidden; }
  .goal-cat { flex: none; width: 0.9in; background: var(--main); color: #fff; font-family: var(--display); font-weight: 600;
    display: flex; align-items: center; justify-content: center; font-size: 10pt; }
  .goal-body { flex: 1; padding: 6px 10px 5px; }
  .goal-body .blank { height: 0.3in; display: block; }
  .goal-body .ideas { font-size: 7pt; color: var(--muted); margin-top: 3px; }

  .week-head { display: flex; align-items: flex-end; justify-content: space-between; margin-bottom: 8px; }
  .week-head .kicker { font-size: 8pt; font-weight: 700; letter-spacing: 0.12em; text-transform: uppercase; color: var(--main); }
  .week-head h2 { font-size: 17pt; }
  .week-head .field { margin: 0; }
  table.week { width: 100%; border-collapse: collapse; table-layout: fixed; font-size: 8pt; }
  table.week col.c-quest { width: 1.35in; }
  table.week th, table.week td { border: 1px solid var(--rule); height: 0.3in; }
  table.week thead th { background: var(--main); color: #fff; font-family: var(--display); font-weight: 600; font-size: 8.5pt; height: 0.26in; }
  table.week thead th:first-child { background: none; border: none; }
  table.week tbody th { text-align: left; padding: 0 5px; font-weight: 600; white-space: nowrap; }
  table.week tbody th .pts { float: right; }
  table.week td.off { background: repeating-linear-gradient(45deg, #eef0f3 0 4px, #e2e6ea 4px 8px); }
  table.week tr.total th { background: var(--tint); font-family: var(--display); }
  table.week tr.total td { background: var(--tint); vertical-align: bottom; text-align: right; padding: 1px 3px; }
  table.week .of { font-size: 6.5pt; color: var(--muted); }
  .week-total { display: grid; grid-template-columns: 1fr 1fr; gap: 0 14px; margin-top: 8px; padding: 6px 10px 8px;
    border: 2px solid var(--main); border-radius: 10px; }

  table.wrap th { width: 1.8in; }
  table.wrap tr.sum th, table.wrap tr.sum td { background: var(--tint); font-family: var(--display); font-size: 10pt; }
'''


def build():
    # Winged Lion patch, shrunk for print (macOS sips) so the PDF stays small.
    subprocess.run(["sips", "-Z", "900", str(ROOT / "awards" / "winged-lion-patch.jpg"), "--out", str(ROOT / PATCH)], check=True, capture_output=True)
    parts = [cover(), goals_page()] + [week_page(n) for n in range(1, 5)] + [wrapup(), badge_menu_page()]
    doc = f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>CoreXP Monthly Quest Packet</title>
  <!-- Generated by tools/build_monthly_packet.py. Edit the QUESTS list there, then rebuild. -->
  <link rel="stylesheet" href="assets/booklet.css">
  <style>{STYLE}</style>
</head>
<body>
<div class="print-tip">
  <strong>Printing tip:</strong> Pages are half-letter (5.5″ × 8.5″). Print one packet per adventurer per month, as a booklet or 2 pages per sheet.
</div>
{"".join(parts)}
</body>
</html>
'''
    (ROOT / "School_Year_Packet.html").write_text(doc)
    print(f"Wrote School_Year_Packet.html: {len(parts)} pages, {day_xp(0)} XP/school day, {WEEK_XP} XP/week")


if __name__ == "__main__":
    build()
