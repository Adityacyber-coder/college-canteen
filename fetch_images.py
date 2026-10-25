#!/usr/bin/env python3
"""
Download a real photo for every dish in index.html into ./images/

1. Get a free API key at https://www.pexels.com/api/  (takes a minute)
2. Run:   PEXELS_KEY=your_key_here python3 fetch_images.py
   (Windows PowerShell:  $env:PEXELS_KEY="your_key_here"; python fetch_images.py)
3. Check the photos, replace any you don't like, then deploy.

Options:  --dry    show the search for each dish without downloading
          --force  re-download photos that already exist
Photos come from Pexels (free to use). Photographers are listed in images/CREDITS.txt.
No extra packages needed, only Python 3.
"""
import json, os, re, sys, time, urllib.parse, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "images")
KEY = os.environ.get("PEXELS_KEY", "")
DRY, FORCE = "--dry" in sys.argv, "--force" in sys.argv

# better search words for dishes that are hard to find by name alone
QUERY = {
    "Kanda Poha": "poha indian breakfast",
    "Sabudana Khichdi": "sabudana khichdi",
    "Thalipeeth": "thalipeeth maharashtrian",
    "Sabudana Vada": "sabudana vada",
    "Kothimbir Vadi": "kothimbir vadi",
    "Sheera": "suji halwa sheera",
    "Idli Sambar": "idli sambar",
    "Medu Vada": "medu vada sambar",
    "Maharashtrian Thali": "indian veg thali",
    "Pithla Bhakri": "pithla bhakri",
    "Zunka Bhakar": "zunka bhakri",
    "Varan Bhaat": "dal rice indian",
    "Bharli Vangi Meal": "stuffed brinjal curry indian",
    "Paneer Butter Masala Meal": "paneer butter masala",
    "Dal Khichdi": "dal khichdi",
    "Misal Pav": "misal pav",
    "Usal Pav": "usal pav",
    "Batata Vada": "batata vada",
    "Kanda Bhaji": "onion pakoda bhaji",
    "Ragda Pattice": "ragda pattice",
    "Bhel Puri": "bhel puri",
    "Bombay Sandwich": "bombay veg sandwich",
    "Pav Bhaji": "pav bhaji",
    "Pani Puri": "pani puri golgappa",
    "Veg Momos": "veg momos",
    "Cutting Chai": "masala chai glass",
    "Sol Kadhi": "sol kadhi",
    "Masala Taak": "masala chaas buttermilk",
    "Aamras": "aamras mango pulp",
    "Kokum Sharbat": "kokum sherbet",
    "Puran Poli": "puran poli",
    "Modak": "modak ganesh sweet",
    "Shrikhand": "shrikhand",
    "Basundi": "basundi rabdi",
    "Gulab Jamun": "gulab jamun",
    "Filter Coffee": "south indian filter coffee",
}


def slug(n):
    n = re.sub(r"\(.*?\)", "", n.lower())
    return re.sub(r"^-|-$", "", re.sub(r"[^a-z0-9]+", "-", n))


def clean(n):
    return re.sub(r"\s*\(.*?\)", "", n).strip()


def names():
    src = open(os.path.join(HERE, "index.html"), encoding="utf-8").read()
    return re.findall(r'mk\(\d+,"([^"]+)"', src)


def get(url, headers=None):
    req = urllib.request.Request(url, headers=headers or {"User-Agent": "canteen-app"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()


def main():
    if not DRY and not KEY:
        sys.exit("Set your free Pexels key first:  PEXELS_KEY=xxxx python3 fetch_images.py")
    os.makedirs(OUT, exist_ok=True)
    credits, ok, miss = [], 0, []
    for n in names():
        f = os.path.join(OUT, slug(n) + ".jpg")
        q = QUERY.get(clean(n), clean(n) + " indian food")
        if DRY:
            print(f"{slug(n)+'.jpg':34} <- search: {q}")
            continue
        if os.path.exists(f) and not FORCE:
            print("skip (exists)", n)
            continue
        try:
            url = "https://api.pexels.com/v1/search?" + urllib.parse.urlencode(
                {"query": q, "per_page": 1, "orientation": "landscape"})
            data = json.loads(get(url, {"Authorization": KEY, "User-Agent": "canteen-app"}))
            if not data.get("photos"):
                miss.append(n); print("no photo found:", n); continue
            ph = data["photos"][0]
            open(f, "wb").write(get(ph["src"]["medium"]))
            credits.append(f"{slug(n)}.jpg - {ph.get('photographer','?')} - {ph['url']}")
            ok += 1; print("saved", n)
        except Exception as e:
            miss.append(n); print("failed:", n, e)
        time.sleep(0.4)
    if not DRY:
        with open(os.path.join(OUT, "CREDITS.txt"), "a", encoding="utf-8") as c:
            c.write("\n".join(credits) + "\n")
        print(f"\nDone: {ok} photos saved, {len(miss)} missing (those keep the drawn picture).")
        if miss:
            print("Missing:", ", ".join(miss))


main()
