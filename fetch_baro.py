# fetch_baro.py — run by GitHub Actions daily
# Fetches Baro Ki'teer item prices from warframe.market v2 → prices_baro.json
#
# MODS: two calls each — ?rank=0 (unranked) and ?rank=<max_rank> (maxed).
#       The v2 /top endpoint filters by the `rank` query param.
#
# WEAPONS: single call, no rank param.
#
# Orokin slug note: WFM still uses pre-Jade-Shadows "corrupted" slugs for the
#   four Orokin faction mods (Bane/Cleanse/Expel/Smite of Orokin).
#   Display names use the current in-game names; slugs use the old WFM names.
#   When WFM updates their slugs, just replace the slug strings below.

import json
import time
import urllib.request
from datetime import datetime, timezone

# ── MOD MAX RANKS ─────────────────────────────────────────────────────────────
# Primed mods = rank 10. Non-primed Baro mods = rank 5. Peculiar = rank 3.
MOD_MAX_RANKS = {
    # rank 3 mods
    "primed_chamber" : 3, "astral_twilight" : 3, "jolt": 3, "scorch": 3, "scattering_inferno": 3, "shell_shock": 3,
     "tempo_royale": 3,
    "thermite_rounds": 3, "vermillion_storm": 3, "volcanic_edge": 3,
    "voltaic_strike": 3, "high_voltage": 3,
    # Non-primed Baro exclusives — rank 5
    "buzz_kill": 5, "collision_force": 5,
    "combo_fury": 5, "combo_killer": 5, "crash_course": 5,
    "fanged_fusillade": 5, "full_contact": 5, 
    "maim": 5, "mark_of_the_beast": 5, "pummel": 5,
    
    "split_flights": 5, "sweeping_serration": 5,
    
    "peculiar_audience": 5,
    # Everything else defaults to 10 (Primed mods)
}

def max_rank(slug):
    return MOD_MAX_RANKS.get(slug, 10)

# ── MOD LIST ──────────────────────────────────────────────────────────────────
# (display_name, wfm_slug)
BARO_MODS = [
    ("Astral Twilight",              "astral_twilight"),
    ("Buzz Kill",                    "buzz_kill"),
    ("Collision Force",              "collision_force"),
    ("Combo Fury",                   "combo_fury"),
    ("Combo Killer",                 "combo_killer"),
    ("Crash Course",                 "crash_course"),
    ("Fanged Fusillade",             "fanged_fusillade"),
    ("Full Contact",                 "full_contact"),
    ("High Voltage",                 "high_voltage"),
    ("Jolt",                         "jolt"),
    ("Maim",                         "maim"),
    ("Mark of the Beast",            "mark_of_the_beast"),
    ("Primed Ammo Stock",            "primed_ammo_stock"),
    ("Primed Animal Instinct",       "primed_animal_instinct"),
    ("Primed Bane of Corpus",        "primed_bane_of_corpus"),
    ("Primed Bane of Grineer",       "primed_bane_of_grineer"),
    ("Primed Bane of Infested",      "primed_bane_of_infested"),
    ("Primed Bane of Orokin",        "primed_bane_of_corrupted"),   # old WFM slug
    ("Primed Chamber",               "primed_chamber"),
    ("Primed Charged Shell",         "primed_charged_shell"),
    ("Primed Chilling Grasp",        "primed_chilling_grasp"),
    ("Primed Cleanse Corpus",        "primed_cleanse_corpus"),
    ("Primed Cleanse Grineer",       "primed_cleanse_grineer"),
    ("Primed Cleanse Infested",      "primed_cleanse_infested"),
    ("Primed Cleanse Orokin",        "primed_cleanse_corrupted"),   # old WFM slug
    ("Primed Continuity",            "primed_continuity"),
    ("Primed Convulsion",            "primed_convulsion"),
    ("Primed Counterbalance",        "primed_counterbalance"),
    ("Primed Cryo Rounds",           "primed_cryo_rounds"),
    ("Primed Deadly Efficiency",     "primed_deadly_efficiency"),
    ("Primed Dual Rounds",           "primed_dual_rounds"),
    ("Primed Expel Corpus",          "primed_expel_corpus"),
    ("Primed Expel Grineer",         "primed_expel_grineer"),
    ("Primed Expel Infested",        "primed_expel_infested"),
    ("Primed Expel Orokin",          "primed_expel_corrupted"),     # old WFM slug
    ("Primed Fast Hands",            "primed_fast_hands"),
    ("Primed Fever Strike",          "primed_fever_strike"),
    ("Primed Firestorm",             "primed_firestorm"),
    ("Primed Flow",                  "primed_flow"),
    ("Primed Fulmination",           "primed_fulmination"),
    ("Primed Heated Charge",         "primed_heated_charge"),
    ("Primed Heavy Trauma",          "primed_heavy_trauma"),
    ("Primed Magazine Warp",         "primed_magazine_warp"),
    ("Primed Morphic Transformer",   "primed_morphic_transformer"),
    ("Primed Pack Leader",           "primed_pack_leader"),
    ("Primed Pistol Ammo Mutation",  "primed_pistol_ammo_mutation"),
    ("Primed Pistol Gambit",         "primed_pistol_gambit"),
    ("Primed Point Blank",           "primed_point_blank"),
    ("Primed Pressure Point",        "primed_pressure_point"),
    ("Primed Quickdraw",             "primed_quickdraw"),
    ("Primed Ravage",                "primed_ravage"),
    ("Primed Reach",                 "primed_reach"),
    ("Primed Redirection",           "primed_redirection"),
    ("Primed Regen",                 "primed_regen"),
    ("Primed Rifle Ammo Mutation",   "primed_rifle_ammo_mutation"),
    ("Primed Rubedo-Lined Barrel",   "primed_rubedo_lined_barrel"),
    ("Primed Shotgun Ammo Mutation", "primed_shotgun_ammo_mutation"),
    ("Primed Slip Magazine",         "primed_slip_magazine"),
    ("Primed Smite Corpus",          "primed_smite_corpus"),
    ("Primed Smite Grineer",         "primed_smite_grineer"),
    ("Primed Smite Infested",        "primed_smite_infested"),
    ("Primed Smite Orokin",          "primed_smite_corrupted"),     # old WFM slug
    ("Primed Smite the Murmur",      "primed_smite_the_murmur"),
    ("Primed Sniper Ammo Mutation",  "primed_sniper_ammo_mutation"),
    ("Primed Stabilizer",            "primed_stabilizer"),
    ("Primed Steady Hands",          "primed_steady_hands"),
    ("Primed Tactical Pump",         "primed_tactical_pump"),
    ("Primed Target Cracker",        "primed_target_cracker"),
    ("Pummel",                       "pummel"),
    ("Scattering Inferno",           "scattering_inferno"),
    ("Scorch",                       "scorch"),
    ("Shell Shock",                  "shell_shock"),
    ("Split Flights",                "split_flights"),
    ("Sweeping Serration",           "sweeping_serration"),
    ("Tempo Royale",                 "tempo_royale"),
    ("Thermite Rounds",              "thermite_rounds"),
    ("Vermillion Storm",             "vermillion_storm"),
    ("Volcanic Edge",                "volcanic_edge"),
    ("Voltaic Strike",               "voltaic_strike"),
    ("Peculiar Audience",            "peculiar_audience"),
]

# ── WEAPON LIST ───────────────────────────────────────────────────────────────
BARO_WEAPONS = [
    ("Glaxion Vandal",          "glaxion_vandal"),
    ("Gotva Prime",             "gotva_prime"),
    ("Halikar Wraith",          "halikar_wraith"),
    ("Ignis Wraith",            "ignis_wraith"),
    ("Machete Wraith",          "machete_wraith"),
    ("Mara Detron",             "mara_detron"),
    ("Opticor Vandal",          "opticor_vandal"),
    ("Prisma Angstrum",         "prisma_angstrum"),
    ("Prisma Dual Cleavers",    "prisma_dual_cleavers"),
    ("Prisma Dual Decurions",   "prisma_dual_decurions"),
    ("Prisma Gorgon",           "prisma_gorgon"),
    ("Prisma Grakata",          "prisma_grakata"),
    ("Prisma Grinlok",          "prisma_grinlok"),
    ("Prisma Lenz",             "prisma_lenz"),
    ("Prisma Machete",          "prisma_machete"),
    ("Prisma Obex",             "prisma_obex"),
    ("Prisma Ohma",             "prisma_ohma"),
    ("Prisma Skana",            "prisma_skana"),
    ("Prisma Tetra",            "prisma_tetra"),
    ("Prisma Twin Gremlins",    "prisma_twin_gremlins"),
    ("Prisma Veritux",          "prisma_veritux"),
    ("Prova Vandal",            "prova_vandal"),
    ("Quanta Vandal",           "quanta_vandal"),
    ("Supra Vandal",            "supra_vandal"),
    ("Vastilok",                "vastilok"),
    ("Vericres",                "vericres"),
    ("Viper Wraith",            "viper_wraith"),
    ("Vulkar Wraith",           "vulkar_wraith"),
    ("Zylok",                   "zylok"),
]

# ── OTHER LIST (relics + key) ─────────────────────────────────────────────────
# (display_name, wfm_slug)
# Note: Neo O1 uses letter O, not zero. Key slug has literal "(key)" in it.
BARO_OTHER = [
    ("Axi A2 Relic",     "axi_a2_relic"),
    ("Axi A5 Relic",     "axi_a5_relic"),
    ("Axi M5 Relic",     "axi_m5_relic"),
    ("Axi V8 Relic",     "axi_v8_relic"),
    ("Neo O1 Relic",     "neo_o1_relic"),
    ("Baro Void-Signal", "baro_void_signal_(key)"),
]

HEADERS = {
    "Platform": "pc",
    "Language": "en",
    "User-Agent": "WarframeWeekly/1.0",
}

def fetch_orders(slug, rank=None):
    """
    Fetch top sell orders for an item.
    rank=None  → no filter (weapons)
    rank=0     → unranked mod orders only
    rank=N     → rank-N mod orders only (e.g. rank=10 for maxed Primed mods)

    The v2 /top endpoint accepts `rank` as a numeric query parameter and
    returns only orders matching that rank.
    """
    url = f"https://api.warframe.market/v2/orders/item/{slug}/top"
    if rank is not None:
        url += f"?rank={rank}"

    req = urllib.request.Request(url, headers=HEADERS)
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
        print(f"    ERROR ({slug}, rank={rank}): {e}")
        return None

# ── FETCH MODS ────────────────────────────────────────────────────────────────
print(f"Fetching {len(BARO_MODS)} mods (rank=0 unranked + rank=max maxed)...")
mod_results = []

for name, slug in BARO_MODS:
    print(f"  {name}...", end=" ", flush=True)

    price_unranked = fetch_orders(slug, rank=0)
    time.sleep(0.35)
    price_maxed = fetch_orders(slug, rank=max_rank(slug))
    time.sleep(0.35)

    if price_unranked is not None or price_maxed is not None:
        mod_results.append({
            "name":           name,
            "slug":           slug,
            "price_unranked": price_unranked,
            "price_maxed":    price_maxed,
        })
        parts = []
        if price_unranked is not None: parts.append(f"unranked={price_unranked}")
        if price_maxed    is not None: parts.append(f"maxed={price_maxed}")
        print(", ".join(parts))
    else:
        print("skipped")

mod_results.sort(
    key=lambda x: x["price_maxed"] if x["price_maxed"] is not None else x["price_unranked"] or 0,
    reverse=True
)

# ── FETCH WEAPONS ─────────────────────────────────────────────────────────────
print(f"\nFetching {len(BARO_WEAPONS)} weapons...")
weapon_results = []

for name, slug in BARO_WEAPONS:
    print(f"  {name}...", end=" ", flush=True)
    price = fetch_orders(slug)
    time.sleep(0.35)
    if price is not None:
        weapon_results.append({"name": name, "slug": slug, "avg_price": price})
        print(price)
    else:
        print("skipped")

weapon_results.sort(key=lambda x: x["avg_price"], reverse=True)

# ── FETCH OTHER (relics + key) ────────────────────────────────────────────────
print(f"\nFetching {len(BARO_OTHER)} other items (relics + key)...")
other_results = []

for name, slug in BARO_OTHER:
    print(f"  {name}...", end=" ", flush=True)
    price = fetch_orders(slug)
    time.sleep(0.35)
    other_results.append({"name": name, "slug": slug, "avg_price": price})
    print(price if price is not None else "no listings")

# ── SAVE ──────────────────────────────────────────────────────────────────────
output = {
    "updated": datetime.now(timezone.utc).isoformat(),
    "mods":    mod_results,
    "weapons": weapon_results,
    "other":   other_results,
}

with open("prices_baro.json", "w") as f:
    json.dump(output, f, indent=2)

print(f"\nDone!")
print(f"  Mods:    {len(mod_results)}/{len(BARO_MODS)}")
print(f"  Weapons: {len(weapon_results)}/{len(BARO_WEAPONS)}")
print(f"  Other:   {len(other_results)}/{len(BARO_OTHER)}")
