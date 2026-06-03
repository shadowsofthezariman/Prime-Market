# fetch_weapons.py — run by GitHub Actions daily
# Fetches Warframe Prime Weapon prices from warframe.market → prices_weapons.json
#
# Each entry: (slug, display_name, category, custom_item_slug)
#   custom_item_slug — if set, overrides the default "{slug}_prime_set" URL.
#                      Use this for Baro items, single-piece primes, etc.
#   e.g. Gotva Prime is sold by Baro as a single item → "gotva_prime"

import json
import time
import urllib.request
from datetime import datetime, timezone

WEAPON_SETS = [
    # ── PRIMARY ──────────────────────────────────────────────────────────────
    ("acceltra",          "Acceltra",          "primary",   None),
    ("alternox",          "Alternox",          "primary",   None),
    ("astilla",           "Astilla",           "primary",   None),
    ("baza",              "Baza",              "primary",   None),
    ("boar",              "Boar",              "primary",   None),
    ("boltor",            "Boltor",            "primary",   None),
    ("braton",            "Braton",            "primary",   None),
    ("burston",           "Burston",           "primary",   None),
    ("cedo",              "Cedo",              "primary",   None),
    ("cernos",            "Cernos",            "primary",   None),
    ("corinth",           "Corinth",           "primary",   None),
    ("daikyu",            "Daikyu",            "primary",   None),
    ("fulmin",            "Fulmin",            "primary",   None),
    ("gotva",             "Gotva",             "primary",   "gotva_prime"),   # Baro item, no _set
    ("latron",            "Latron",            "primary",   None),
    ("nagantaka",         "Nagantaka",         "primary",   None),
    ("panthera",          "Panthera",          "primary",   None),
    ("paris",             "Paris",             "primary",   None),
    ("perigale",          "Perigale",          "primary",   None),
    ("phantasma",         "Phantasma",         "primary",   None),
    ("rubico",            "Rubico",            "primary",   None),
    ("scourge",           "Scourge",           "primary",   None),
    ("soma",              "Soma",              "primary",   None),
    ("stradavar",         "Stradavar",         "primary",   None),
    ("strun",             "Strun",             "primary",   None),
    ("sybaris",           "Sybaris",           "primary",   None),
    ("tenora",            "Tenora",            "primary",   None),
    ("tiberon",           "Tiberon",           "primary",   None),
    ("tigris",            "Tigris",            "primary",   None),
    ("trumna",            "Trumna",            "primary",   None),
    ("vadarya",           "Vadarya",           "primary",   None),
    ("vectis",            "Vectis",            "primary",   None),
    ("zhuge",             "Zhuge",             "primary",   None),

    # ── SECONDARY ────────────────────────────────────────────────────────────
    ("afuris",            "Afuris",            "secondary", None),
    ("akarius",           "Akarius",           "secondary", None),
    ("akbolto",           "Akbolto",           "secondary", None),
    ("akbronco",          "Akbronco",          "secondary", None),
    ("akjagara",          "Akjagara",          "secondary", None),
    ("aklex",             "Aklex",             "secondary", None),
    ("akmagnus",          "Akmagnus",          "secondary", None),
    ("aksomati",          "Aksomati",          "secondary", None),
    ("akstiletto",        "Akstiletto",        "secondary", None),
    ("akvasto",           "Akvasto",           "secondary", None),
    ("ballistica",        "Ballistica",        "secondary", None),
    ("bronco",            "Bronco",            "secondary", None),
    ("epitaph",           "Epitaph",           "secondary", None),
    ("euphona",           "Euphona",           "secondary", None),
    ("hikou",             "Hikou",             "secondary", None),
    ("hystrix",           "Hystrix",           "secondary", None),
    ("knell",             "Knell",             "secondary", None),
    ("kompressa",         "Kompressa",         "secondary", None),
    ("lato",              "Lato",              "secondary", None),
    ("lex",               "Lex",               "secondary", None),
    ("magnus",            "Magnus",            "secondary", None),
    ("pandero",           "Pandero",           "secondary", None),
    ("pyrana",            "Pyrana",            "secondary", None),
    ("sagek",             "Sagek",             "secondary", None),
    ("sicarus",           "Sicarus",           "secondary", None),
    ("spira",             "Spira",             "secondary", None),
    ("vasto",             "Vasto",             "secondary", None),
    ("velox",             "Velox",             "secondary", None),
    ("zakti",             "Zakti",             "secondary", None),
    ("zylok",             "Zylok",             "secondary", None),

    # ── MELEE ────────────────────────────────────────────────────────────────
    ("ankyros",           "Ankyros",           "melee",     None),
    ("bo",                "Bo",                "melee",     None),
    ("cobra_and_crane",   "Cobra & Crane",     "melee",     None),
    ("dakra",             "Dakra",             "melee",     None),
    ("destreza",          "Destreza",          "melee",     None),
    ("dual_kamas",        "Dual Kamas",        "melee",     None),
    ("dual_keres",        "Dual Keres",        "melee",     None),
    ("dual_zoren",        "Dual Zoren",        "melee",     None),
    ("fang",              "Fang",              "melee",     None),
    ("fragor",            "Fragor",            "melee",     None),
    ("galariak",          "Galariak",          "melee",     None),
    ("galatine",          "Galatine",          "melee",     None),
    ("glaive",            "Glaive",            "melee",     None),
    ("gram",              "Gram",              "melee",     None),
    ("guandao",           "Guandao",           "melee",     None),
    ("gunsen",            "Gunsen",            "melee",     None),
    ("karyst",            "Karyst",            "melee",     None),
    ("kestrel",           "Kestrel",           "melee",     None),
    ("kogake",            "Kogake",            "melee",     None),
    ("kronen",            "Kronen",            "melee",     None),
    ("masseter",          "Masseter",          "melee",     None),
    ("nami_skyla",        "Nami Skyla",        "melee",     None),
    ("nikana",            "Nikana",            "melee",     None),
    ("ninkondi",          "Ninkondi",          "melee",     None),
    ("okina",             "Okina",             "melee",     None),
    ("orthos",            "Orthos",            "melee",     None),
    ("pangolin",          "Pangolin",          "melee",     None),
    ("quassus",           "Quassus",           "melee",     None),
    ("reaper",            "Reaper",            "melee",     None),
    ("redeemer",          "Redeemer",          "melee",     None),
    ("sarofang",          "Sarofang",          "melee",     None),
    ("scindo",            "Scindo",            "melee",     None),
    ("silva_and_aegis",   "Silva & Aegis",     "melee",     None),
    ("skana",             "Skana",             "melee",     None),
    ("tatsu",             "Tatsu",             "melee",     None),
    ("tekko",             "Tekko",             "melee",     None),
    ("tipedo",            "Tipedo",            "melee",     None),
    ("venato",            "Venato",            "melee",     None),
    ("venka",             "Venka",             "melee",     None),
    ("volnus",            "Volnus",            "melee",     None),

    # ── ARCHGUN ──────────────────────────────────────────────────────────────
    ("corvas",            "Corvas",            "archgun",   None),
    ("larkspur",          "Larkspur",          "archgun",   None),

    # ── COMPANION ────────────────────────────────────────────────────────────
    ("carrier",           "Carrier",           "companion", None),
    ("dethcube",          "Dethcube",          "companion", None),
    ("helios",            "Helios",            "companion", None),
    ("nautilus",          "Nautilus",          "companion", None),
    ("shade",             "Shade",             "companion", None),
    ("wyrm",              "Wyrm",              "companion", None),

    # ── ARCHWING ─────────────────────────────────────────────────────────────
    ("odonata",           "Odonata",           "archwing",  None),
]

def fetch_price(slug, custom_item_slug=None):
    item_id = custom_item_slug if custom_item_slug else f"{slug}_prime_set"
    url = f"https://api.warframe.market/v2/orders/item/{item_id}/top"
    req = urllib.request.Request(url, headers={
        "Platform": "pc",
        "Language": "en",
        "User-Agent": "WarframeWeekly/1.0"
    })
    try:
        with urllib.request.urlopen(req, timeout=10) as res:
            data = json.loads(res.read())
        sell_orders = data.get("data", {}).get("sell", [])
        prices = [
            o.get("platinum") or o.get("price")
            for o in sell_orders
            if o.get("user", {}).get("status") == "ingame"
            and (o.get("platinum") or o.get("price"))
        ]
        return round(sum(prices) / len(prices)) if prices else None
    except Exception as e:
        print(f"  ERROR: {e}")
        return None

# ── FETCH ─────────────────────────────────────────────────────────────────
by_category = {c: [] for c in ["primary","secondary","melee","archgun","companion","archwing"]}

print(f"Fetching prices for {len(WEAPON_SETS)} Prime weapon sets...")

for slug, name, category, custom in WEAPON_SETS:
    tag = f"[Baro/{custom}]" if custom else f"[{slug}_prime_set]"
    print(f"  [{category:10}] {name} {tag}...", end=" ", flush=True)
    price = fetch_price(slug, custom)
    if price:
        by_category[category].append({"slug": slug, "name": name, "avg_price": price, "custom_url": custom})
        print(price)
    else:
        print("skipped")
    time.sleep(0.4)

# ── PROCESS ───────────────────────────────────────────────────────────────
def top_n(items, n, reverse=True):
    return sorted(items, key=lambda x: x["avg_price"], reverse=reverse)[:n]

all_items = [item for cat in by_category.values() for item in cat]

output = {
    "updated": datetime.now(timezone.utc).isoformat(),
    "overall": {
        "expensive": top_n(all_items, 10),
        "cheapest":  top_n(all_items, 10, reverse=False),
    },
    "primary":   {"expensive": top_n(by_category["primary"],   10), "cheapest": top_n(by_category["primary"],   10, False)},
    "secondary": {"expensive": top_n(by_category["secondary"], 10), "cheapest": top_n(by_category["secondary"], 10, False)},
    "melee":     {"expensive": top_n(by_category["melee"],     10), "cheapest": top_n(by_category["melee"],     10, False)},
    "archgun":   {"all": top_n(by_category["archgun"],   99)},
    "companion": {"all": top_n(by_category["companion"], 99)},
    "archwing":  {"all": top_n(by_category["archwing"],  99)},
}

with open("prices_weapons.json", "w") as f:
    json.dump(output, f, indent=2)

print(f"\nDone! {len(all_items)}/{len(WEAPON_SETS)} items saved to prices_weapons.json")
