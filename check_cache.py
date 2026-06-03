import json

with open("data/sofascore_cache.json", encoding="utf-8") as f:
    c = json.load(f)

stats = c.get("stats", {})
filled = [k for k, v in stats.items() if v]

print(f"Stats totali in cache: {len(stats)}")
print(f"Stats con dati: {len(filled)}")

if filled:
    # Mostra un esempio
    key = filled[0]
    print(f"\nEsempio stat ({key}):")
    print(json.dumps(c["stats"][key], indent=2)[:300])
    