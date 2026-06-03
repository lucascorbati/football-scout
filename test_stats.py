import requests
import json

API_KEY = "50c70d0683msh02eabcbb3d2a140p14ba5fjsn24a732e88f96"
HEADERS = {
    "x-rapidapi-key": API_KEY,
    "x-rapidapi-host": "sofascore.p.rapidapi.com"
}

# Usa un ID trovato dalla cache — Brenden Aaronson
pid = 973431

url = f"https://sofascore.p.rapidapi.com/players/get-all-statistics?playerId={pid}"
r = requests.get(url, headers=HEADERS, timeout=15)
print(f"Status: {r.status_code}")
data = r.json()

seasons = data.get("seasons", [])
print(f"Stagioni totali: {len(seasons)}")

TOP5 = {17, 8, 23, 35, 34}
SEASON_2526 = {17: 76986, 8: 77559, 23: 76457, 35: 77333, 34: 77356}

for s in seasons:
    t_id = s.get("uniqueTournament", {}).get("id")
    year = s.get("year", "")
    s_id = s.get("id", 0)
    t_name = s.get("uniqueTournament", {}).get("name", "")
    print(f"  torneo={t_name}(id={t_id}) year={year} season_id={s_id}")
    if t_id in TOP5 and year == "25/26":
        print(f"  ✅ TROVATO! Stats: {list(s.get('statistics', {}).keys())[:5]}")