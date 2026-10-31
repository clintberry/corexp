# CoreXP: Life Skills Adventure Program

**CoreXP** is a custom, badge-based life skills program designed to help kids build real-world confidence, character, and capability. Inspired by the best parts of scouting, gamification, and personal development, CoreXP empowers kids through exploration, challenge, and reflection.

---

## 🌟 Program Goals

- Teach essential life skills across multiple domains (character, health, creativity, etc.)
- Encourage independent learning and personal growth
- Strengthen family relationships through shared experiences and mentorship
- Make learning fun, meaningful, and memorable

---

## 🧭 Badge Categories

CoreXP is divided into **seven badge categories**, each representing a pillar of lifelong development:

1. **Character & Spirituality** – Values, service, spiritual habits
2. **Health & Physical Wellness** – Fitness, hygiene, nutrition, first aid
3. **Emotional & Mental Resilience** – Mindset, mindfulness, self-reflection
4. **Relationships & Social Skills** – Communication, empathy, teamwork
5. **Practical Life Skills** – Cooking, organizing, money, safety
6. **Creativity & Innovation** – Art, music, design, storytelling, coding
7. **Nature & Citizenship** – Outdoor skills, service, civic engagement

---

## 🎖 Badge Format

Each badge includes **three levels** of progression:

- **Explorer** – Awareness and first experiences
- **Builder** – Skill-building and independent application
- **Master** – Mastery, leadership, and reflection

Each level contains multiple tasks that encourage action, thought, and creativity.

Finishing the 22 required badges at a level, plus 6 electives (at least 2 from Creativity & Innovation) and three Epic Quests of the matching tier, earns that **level patch**: Explorer takes 3 Challenger quests, Builder 3 Champion quests, and Master 3 Legend quests. The Master patch unlocks the top award, which requires a major service project. See [`CoreXP_Awards.md`](CoreXP_Awards.md).

---

## ⚡ XP & Epic Quests

Every requirement earns **XP** when it's finished and signed off, so badges plug straight into a daily XP system like SummerXP. XP is based on how much effort a requirement takes:

| Size | XP | What it looks like |
|---|---|---|
| Quick | **2** | One sitting: name, learn, talk about, or share something |
| Task | **5** | Make, write, practice, or roleplay something, or repeat a habit for 2–5 days |
| Project | **10** | Plan and complete something, teach, lead, interview, present, or keep a habit for about a week |
| Challenge | **20** | Keep a habit for 2–4 weeks, or finish a major project or certification |
| Marathon | **40** | Keep a habit for 2+ months |

Each badge also has three optional **Epic Quests**: stretch goals beyond the requirements, each earned once.

| Tier | XP |
|---|---|
| ★ Challenger | 15 |
| ★★ Champion | 25 |
| ★★★ Legend | 40 |

Epic Quests can be earned any time, even before a level is finished.

### XP Tracker booklet

[`XP_Tracker.pdf`](XP_Tracker.pdf) is one printable booklet that logs XP for every badge. It has a cover showing the four big awards, a scoreboard that marks the elective badges, a divider page for each category, and a page per badge listing every requirement and Epic Quest with its XP, a checkbox, a date, and mentor initials.

It's generated from the badge markdown files, so rebuild it after changing any requirements or XP:

```
python3 tools/build_xp_tracker.py
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless --no-pdf-header-footer --print-to-pdf=XP_Tracker.pdf XP_Tracker.html
```

---

## 📂 Repository Structure

```
CoreXP_Badges/
│
├── Character_Spirituality/
├── Health_Physical_Wellness/
├── Emotional_Mental_Resilience/
├── Relationships_Social_Skills/
├── Practical_Life_Skills/
├── Creativity_Innovation/
├── Nature_Citizenship/
│
└── CoreXP_Badge_Index.md     # A full list of all badge files
```

Each badge is stored as a markdown file with:
- A description and purpose
- Level-based requirements
- Reflection and teaching components

### Badge folders

Every badge lives in its own folder with its definition and logo. Character & Spirituality also has printable booklets and an alternate poster-style logo:

```
1. Character & Spirituality/badges/Pathfinder/
├── Pathfinder.md       # Badge definition (source of truth for requirements & XP)
├── logo.svg            # Badge patch artwork
├── logo-poster.svg     # Alternate retro propaganda-poster artwork (Category 1 only, for now)
├── booklet.html        # Printable log booklet (half-letter pages)
└── booklet.pdf         # Rendered booklet, ready to print
```

Booklets share one stylesheet, `assets/booklet.css`; each booklet sets its own colors at the top of the file. To regenerate a PDF, open `booklet.html` in Chrome and print to PDF (margins: default, headers/footers off), or run:

```
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless --no-pdf-header-footer --print-to-pdf=booklet.pdf booklet.html
```

Print the PDF as a booklet (or 2 pages per letter sheet) and fold.

---

## 📅 CoreXP Daily: School Year

[`School_Year_Packet.pdf`](School_Year_Packet.pdf) is a monthly packet for daily quests during the school year: a toned-down version of SummerXP with homework as the main daily quest. Print one per adventurer each month. It has:

- Daily quests at a glance on the cover
- A page for setting the month's four daily goals, badge focus, and bonuses
- Four weekly quest charts (Mon–Sun checkboxes, XP totals, a line for badge progress)
- A monthly wrap-up with totals and reflection
- A Badge Menu of every badge on the last page

| Quest | When | XP |
|---|---|---|
| Homework (or 20 min of study if none) | Mon–Fri | 3 |
| Daily goals: Spiritual, Physical, Mental, Social | Spiritual & Social every day, the others Mon–Sat | 1 each |
| Daily chore / Weekend chore | Mon–Fri / Saturday | 1 / 3 |
| Reading (20 min) | Mon–Sat | 1 |
| Music (15 min) | Mon–Fri | 1 |
| Book report / Song performance | Once a month | 10 each |

A school day is worth 10 XP and a full week 60 XP. Badge work isn't on the chart: badges earn their own XP, logged in the XP Tracker. To change the quests or XP, edit the lists at the top of `tools/build_monthly_packet.py` and rebuild it the same way as the XP Tracker.

---

## 📱 CoreXP Tracker app

[`app/index.html`](app/index.html) is a web app for tracking each kid's progress digitally, published as a private claude.ai artifact. For each adventurer it shows:

- A badge wall of all 34 badges. A badge's logo fills in with color as its levels are earned, and a tap opens its checklist of requirements and Epic Quests, dated as they're checked off.
- Total XP and progress toward the Explorer, Builder, and Master level patches (required badges plus electives at that level). Elective badges are marked on the badge wall.
- A **To hand out** queue of physical awards that are earned but not yet given: a level button for each finished level, the badge patch when all three levels are done (mark it ordered, then given), and the level patches.

Progress is saved in the artifact's shared database, so it syncs across devices. The badge list comes from the markdown. After changing badges, rebuild `app/catalog.json` and `app/logos/` and republish the page with them:

```
python3 tools/build_app.py
```

---

## 🛠 How to Use

1. Choose a badge based on your child's interest or a category you want to emphasize.
2. Print the badge file or copy it into a family journal or digital folder.
3. Work on tasks progressively—Explorer → Builder → Master.
4. Award badges using stickers, patches, or digital recognition.
5. Celebrate milestone achievements with level awards (e.g., “All Explorer Badges Completed”).

---

## 🔁 Contributing

This program is evolving! Feel free to:
- Suggest new badges or levels
- Share ideas for printable tools or visuals
- Adapt and remix for your own family or educational setting

---

## ❤️ Created For

Families who want to raise capable, kind, grounded kids—with a sense of purpose, curiosity, and adventure.
