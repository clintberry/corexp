"""Build the data the CoreXP Tracker app reads: app/catalog.json and app/logos/.

Usage:  python3 tools/build_app.py
Then republish app/index.html with catalog.json and logos/ alongside it.
"""
import json
import re
import shutil
import subprocess
from urllib.parse import unquote

from build_xp_tracker import ROOT, load_categories, load_patch_rules

APP = ROOT / "app"
LOGOS = APP / "logos"


def slug(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def clean(text):
    return re.sub(r"\*\*(.+?)\*\*", r"\1", text)


def load_top_award():
    """The top award's name, tagline and numbered requirements, from CoreXP_Awards.md."""
    lines = (ROOT / "CoreXP_Awards.md").read_text().splitlines()
    start = next(i for i, l in enumerate(lines) if l.startswith("## ") and "Award" in l and i > 0 and "Level" not in l)
    name = re.sub(r"^##\s+\S+\s+", "", lines[start]).replace("(working name)", "").strip()
    tagline = next(l.strip("* ") for l in lines[start + 1:] if l.startswith("**"))
    reqs = []
    for l in lines[start:]:
        m = re.match(r"^(\d+)\. (.*)$", l)
        if m:
            reqs.append({"n": m.group(1), "text": clean(m.group(2))})
    return {"name": name, "tagline": clean(tagline), "reqs": reqs}


def main():
    if LOGOS.exists():
        shutil.rmtree(LOGOS)
    LOGOS.mkdir(parents=True)

    cats = load_categories()
    rules = load_patch_rules(cats)
    categories = []
    for cat in cats:
        badges = []
        for b in cat["badges"]:
            s = slug(b["title"])
            shutil.copy(ROOT / unquote(b["logo"]), LOGOS / f"{s}.svg")
            badges.append({
                "id": s,
                "title": b["title"],
                "tagline": clean(b["tagline"]),
                "color": b["color"],
                "required": b["required"],
                "logo": f"logos/{s}.svg",
                "levels": [
                    {"name": lv["name"], "xp": lv["xp"],
                     "reqs": [{"n": n, "text": clean(t), "xp": xp} for n, t, xp in lv["reqs"]]}
                    for lv in b["levels"]
                ],
                "epics": [{"stars": st, "tier": tier, "text": clean(t), "xp": xp} for st, tier, t, xp in b["epics"]],
            })
        categories.append({"num": cat["num"], "name": cat["name"], "color": cat["color"], "badges": badges})

    for lvl in ("explorer", "builder", "master"):
        shutil.copy(ROOT / "level-patches" / f"{lvl}-poster.svg", LOGOS / f"level-{lvl}.svg")
    # Medal photo, shrunk for the web (macOS sips).
    subprocess.run(["sips", "-Z", "720", str(ROOT / "awards" / "winged-lion-medal.jpg"), "--out", str(LOGOS / "winged-lion-medal.jpg")], check=True, capture_output=True)

    (APP / "catalog.json").write_text(json.dumps({"categories": categories, "top": load_top_award(), "epicsPerPatch": 3,
        "patch": {"electives": rules["electives"], "minFrom": rules["min_from"]}}, ensure_ascii=False, indent=1))
    n = sum(len(c["badges"]) for c in categories)
    print(f"Wrote app/catalog.json: {len(categories)} categories, {n} badges, top award: {load_top_award()['name']}")


if __name__ == "__main__":
    main()
