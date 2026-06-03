import json
import os

cache_file = "data/sofascore_cache_v3.json"

if not os.path.exists(cache_file):
    print("❌ Cache v3 non esiste ancora")
else:
    with open(cache_file, encoding="utf-8") as f:
        cache = json.load(f)
    
    ids    = cache.get("player_ids", {})
    stats  = cache.get("stats_v3", {})
    
    found_ids   = {k: v for k, v in ids.items() if v is not None}
    not_found   = {k: v for k, v in ids.items() if v is None}
    filled_stats = {k: v for k, v in stats.items() if v}
    
    print(f"🔍 Player IDs trovati:     {len(found_ids)}/{len(ids)}")
    print(f"❌ Player IDs non trovati: {len(not_found)}")
    print(f"📊 Stats con dati:         {len(filled_stats)}/{len(stats)}")
    
    print(f"\nPrimi 5 IDs trovati:")
    for k, v in list(found_ids.items())[:5]:
        print(f"  {k} → id={v}")
    
    print(f"\nPrimi 5 non trovati:")
    for k in list(not_found.keys())[:5]:
        print(f"  {k}")