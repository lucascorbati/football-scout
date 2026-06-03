"""
explore_api.py
--------------
Script di esplorazione per trovare gli ID Sofascore
dei top 5 campionati europei e delle loro squadre.
"""

import requests
import json
import os

API_KEY = os.environ.get("RAPIDAPI_KEY", "50c70d0683msh02eabcbb3d2a140p14ba5fjsn24a732e88f96")

HEADERS = {
    "x-rapidapi-key": API_KEY,
    "x-rapidapi-host": "sofascore-sport-api.p.rapidapi.com",
    "Content-Type": "application/json"
}

BASE_URL = "https://sofascore-sport-api.p.rapidapi.com/api"

def get_player_stats_seasons(player_id: int):
    """Testa le stats stagionali di un giocatore."""
    url = f"{BASE_URL}/player/{player_id}/statistics/seasons"
    r = requests.get(url, headers=HEADERS)
    return r.json()

def get_player_details(player_id: int):
    """Dettagli anagrafici di un giocatore."""
    url = f"{BASE_URL}/player/{player_id}"
    r = requests.get(url, headers=HEADERS)
    return r.json()

def get_team_players(team_id: int):
    """Lista giocatori di una squadra."""
    url = f"{BASE_URL}/team/{team_id}/players"
    r = requests.get(url, headers=HEADERS)
    return r.json()

# ── Test con giocatori famosi ──────────────────────────────────────────────────
# Proviamo con alcuni ID noti di Sofascore
TEST_PLAYERS = {
    "Salah":   939387,
    "Mbappe":  341188,
    "Haaland": 839956,
}

print("=" * 60)
print("🔍 TEST PLAYER DETAILS")
print("=" * 60)

for name, pid in TEST_PLAYERS.items():
    print(f"\n👤 {name} (ID: {pid})")
    data = get_player_details(pid)
    print(json.dumps(data, indent=2)[:500])  # mostra solo i primi 500 caratteri

print("\n" + "=" * 60)
print("📊 TEST PLAYER STATS SEASONS")
print("=" * 60)

for name, pid in TEST_PLAYERS.items():
    print(f"\n📈 {name} stats seasons:")
    data = get_player_stats_seasons(pid)
    print(json.dumps(data, indent=2)[:500])