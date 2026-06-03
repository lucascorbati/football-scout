import requests
import time

API_KEY = "50c70d0683msh02eabcbb3d2a140p14ba5fjsn24a732e88f96"
HEADERS = {
    "x-rapidapi-key": API_KEY,
    "x-rapidapi-host": "sofascore.p.rapidapi.com"
}

leagues = [
    ("Eredivisie",      37),
    ("Süper Lig",       52),
    ("Liga Portugal",  238),
    ("Pro League BE",   38),
]

for name, tid in leagues:
    url = f"https://sofascore.p.rapidapi.com/tournaments/get-seasons?tournamentId={tid}"
    r = requests.get(url, headers=HEADERS, timeout=15)
    data = r.json()
    seasons = data.get("seasons", [])[:4]
    print(f"\n🏆 {name} (id={tid}):")
    for s in seasons:
        print(f"  season_id={s.get('id')} year={s.get('year')}")
    time.sleep(1)