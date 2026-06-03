# fetch_prices.py — run by GitHub Actions daily
# Fetches Warframe Prime Set prices from warframe.market and saves prices.json

import json
import time
import urllib.request
import urllib.error
from datetime import datetime, timezone

WARFRAME_SETS = [
    "excalibur","frost","mag","ember","rhino","loki","nyx","nova","volt","ash",
    "trinity","saryn","vauban","nekros","valkyr","banshee","oberon","hydroid",
    "mirage","zephyr","limbo","chroma","mesa","equinox","wukong","atlas","ivara",
    "titania","inaros","nezha","octavia","gara","nidus","harrow","garuda","khora",
    "revenant","baruuk","hildryn","wisp","grendel","gauss","protea","xaku",
    "lavos","yareli","caliban","gyre","voruna","styanax","citrine","kullervo"
]

def fetch_price(slug):
    url = f"https://api.warframe.market/v2/orders/item/{slug}_prime_set/top"

    req = urllib.request.Request(url, headers={
        "Platform": "pc",
        "Language": "en",
        "User-Agent": "WarframeWeekly/1.0"
    })

    try:
        with urllib.request.urlopen(req, timeout=10) as res:
            data = json.loads(res.read())

        payload = data.get("data", {})
        sell_orders = payload.get("sell", [])

        sell_prices = []

        for o in sell_orders:
            user = o.get("user", {})
            if user.get("status") == "ingame":
                price = o.get("platinum") or o.get("price")
                if price:
                    sell_prices.append(price)

        if not sell_prices:
            return None

        return round(sum(sell_prices) / len(sell_prices))

    except Exception as e:
        print(f"Error fetching {slug}: {e}")
        return None

results = []
print(f"Fetching prices for {len(WARFRAME_SETS)} Prime sets...")

for slug in WARFRAME_SETS:
    display = slug.replace("_", " ").title()
    print(f"  {display}...", end=" ", flush=True)
    price = fetch_price(slug)
    if price:
        results.append({"slug": slug, "name": display, "avg_price": price})
        print(price)
    else:
        print("skipped")
    time.sleep(0.4)  # be polite to the API

results.sort(key=lambda x: x["avg_price"], reverse=True)

output = {
    "updated": datetime.now(timezone.utc).isoformat(),
    "expensive": results[:10],
    "cheapest":  sorted(results, key=lambda x: x["avg_price"])[:5]
}

with open("prices.json", "w") as f:
    json.dump(output, f, indent=2)

print(f"\nDone! {len(results)} sets saved to prices.json")
