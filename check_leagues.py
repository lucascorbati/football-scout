import requests

API_KEY = "50c70d0683msh02eabcbb3d2a140p14ba5fjsn24a732e88f96"
HEADERS = {
    "x-rapidapi-key": API_KEY,
    "x-rapidapi-host": "sofascore.p.rapidapi.com"
}

# Cerca giocatori noti di quei campionati
test_players = [
    ("Lamine Yamal", "Eredivisie"),      # no, è Barça — test con un giocatore Ajax
    ("Steven Berghuis", "Ajax"),          # Eredivisie
    ("Gyokeres", "Sporting CP"),          # Liga Portugal
    ("Tadic", "Fenerbahce"),             # Turchia
    ("De Ketelaere", "Anderlecht"),      # Belgio
]

for name, team in test_players:
    url = f"https://sofascore.p.rapidapi.com/players/search?name={name}"
    r = requests.get(url, headers=HEADERS, timeout=15)
    players = r.json().get("players", [])
    if players:
        p = players[0]
        print(f"✅ {name}: id={p.get('id')} team={p.get('team',{}).get('name','N/A')}")
    else:
        print(f"❌ {name}: non trovato")