"""
enrich_dataset.py
-----------------
Arricchisce players_cleaned.csv con statistiche da Sofascore API.
Strategia: cerca ogni giocatore per nome, trova l'ID corretto,
scarica le stats stagione 25/26.

Output:
  - output/players_enriched.csv
"""

import os
import time
import json
import unicodedata
import requests
import pandas as pd
import numpy as np

# ── Config ─────────────────────────────────────────────────────────────────────
API_KEY  = "50c70d0683msh02eabcbb3d2a140p14ba5fjsn24a732e88f96"
BASE_URL = "https://sofascore.p.rapidapi.com"
HEADERS  = {
    "x-rapidapi-key":  API_KEY,
    "x-rapidapi-host": "sofascore.p.rapidapi.com",
}

CLEANED_PATH  = os.path.join("output", "players_cleaned.csv")
ENRICHED_PATH = os.path.join("output", "players_enriched.csv")
CACHE_FILE    = os.path.join("data",   "sofascore_cache_v3.json")

# ID tornei top 5 campionati
TOP5_IDS = {17, 8, 23, 35, 34}

# Season IDs 25/26
SEASON_2526 = {17: 76986, 8: 77559, 23: 76457, 35: 77333, 34: 77356}

# Mappa nomi squadre CSV → Sofascore
TEAM_NAME_MAP = {
    "liverpool":           "liverpool fc",
    "manchester utd":      "manchester united",
    "brighton":            "brighton & hove albion",
    "wolves":              "wolverhampton wanderers",
    "west ham":            "west ham united",
    "newcastle":           "newcastle united",
    "tottenham":           "tottenham hotspur",
    "leicester":           "leicester city",
    "ipswich":             "ipswich town",
    "barcelona":           "fc barcelona",
    "atletico madrid":     "atletico madrid",
    "alaves":              "deportivo alaves",
    "girona":              "girona fc",
    "levante":             "levante ud",
    "oviedo":              "real oviedo",
    "milan":               "ac milan",
    "napoli":              "ssc napoli",
    "roma":                "as roma",
    "dortmund":            "borussia dortmund",
    "leverkusen":          "bayer leverkusen",
    "gladbach":            "borussia monchengladbach",
    "freiburg":            "sc freiburg",
    "wolfsburg":           "vfl wolfsburg",
    "hoffenheim":          "tsg hoffenheim",
    "augsburg":            "fc augsburg",
    "mainz 05":            "mainz 05",
    "koln":                "fc koln",
    "union berlin":        "union berlin",
    "heidenheim":          "heidenheim",
    "st pauli":            "st. pauli",
    "stuttgart":           "vfb stuttgart",
    "werder bremen":       "werder bremen",
    "rb leipzig":          "rb leipzig",
    "eintracht frankfurt": "eintracht frankfurt",
    "hamburger sv":        "hamburger sv",
    "bayern munich":       "bayern munich",
    "marseille":           "olympique de marseille",
    "lyon":                "olympique lyonnais",
    "monaco":              "as monaco",
    "lens":                "rc lens",
    "strasbourg":          "rc strasbourg",
    "rennes":              "stade rennais",
    "brest":               "stade brestois",
}

# ── Normalizzazione ────────────────────────────────────────────────────────────
def normalize(s: str) -> str:
    s = s.lower().strip()
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return s

# ── Cache ──────────────────────────────────────────────────────────────────────
def load_cache() -> dict:
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_cache(cache: dict):
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=2, ensure_ascii=False)

# ── API calls con retry ────────────────────────────────────────────────────────
def api_get(url: str, retries: int = 3, wait: float = 5.0):
    for attempt in range(retries):
        try:
            r = requests.get(url, headers=HEADERS, timeout=15)
            if r.status_code == 200:
                return r.json()
            elif r.status_code == 429:
                print(f"      ⏳ Rate limit, aspetto {wait*2}s...")
                time.sleep(wait * 2)
            else:
                return {}
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(wait)
            else:
                print(f"      ⚠️  Errore dopo {retries} tentativi: {e}")
    return {}

# ── Cerca giocatore per nome e squadra ────────────────────────────────────────
def search_player(name: str, team: str) -> int | None:
    """
    Cerca il giocatore per nome e verifica che la squadra corrisponda.
    Restituisce il player_id o None.
    """
    url  = f"{BASE_URL}/players/search?name={requests.utils.quote(name)}"
    data = api_get(url)
    players = data.get("players", [])

    team_norm = normalize(TEAM_NAME_MAP.get(normalize(team), team))

    for p in players:
        p_name = normalize(p.get("name", ""))
        p_team = normalize(p.get("team", {}).get("name", ""))

        # Match esatto nome + squadra
        if normalize(name) == p_name and team_norm in p_team:
            return p.get("id")

    # Secondo tentativo: match parziale squadra
    for p in players:
        p_name = normalize(p.get("name", ""))
        p_team = normalize(p.get("team", {}).get("name", ""))
        name_words = normalize(name).split()

        if all(w in p_name for w in name_words) and team_norm in p_team:
            return p.get("id")

    return None

# ── Scarica stats 25/26 ───────────────────────────────────────────────────────
def get_stats_2526(player_id: int) -> dict:
    url  = f"{BASE_URL}/players/get-all-statistics?playerId={player_id}"
    data = api_get(url)
    seasons = data.get("seasons", [])

    for s in seasons:
        t_id = s.get("uniqueTournament", {}).get("id")
        year = s.get("year", "")

        if t_id not in TOP5_IDS:
            continue
        if year != "25/26":
            continue

        stats = s.get("statistics", {})
        if stats:
            return stats

    return {}

# ── Pipeline principale ────────────────────────────────────────────────────────
def main():
    print("📥 Caricamento players_cleaned.csv...")
    df = pd.read_csv(CLEANED_PATH)
    df = df.reset_index(drop=True)
    print(f"   {len(df)} giocatori caricati\n")

    cache = load_cache()
    id_cache    = cache.get("player_ids", {})
    stats_cache = cache.get("stats_v3",   {})

    results = []
    matched = 0
    missing = 0

    print(f"📊 Ricerca e download stats per {len(df)} giocatori...")

    for i in range(len(df)):
        row   = df.iloc[i]
        pname = str(row["player"])
        tname = str(row["team"])
        key   = f"{normalize(pname)}|{normalize(tname)}"

        # Step 1: trova player_id (con cache)
        if key in id_cache:
            pid = id_cache[key]
        else:
            pid = search_player(pname, tname)
            id_cache[key] = pid
            time.sleep(0.3)

        if not pid:
            results.append({})
            missing += 1
            continue

        # Step 2: scarica stats (con cache)
        cache_key = str(pid)
        if cache_key in stats_cache:
            stats = stats_cache[cache_key]
        else:
            stats = get_stats_2526(pid)
            stats_cache[cache_key] = stats
            time.sleep(0.4)

        results.append(stats)
        if stats:
            matched += 1

        # Salva cache ogni 50 giocatori
        if i % 50 == 0 and i > 0:
            print(f"   ... {i}/{len(df)} processati — matchati: {matched}")
            cache["player_ids"] = id_cache
            cache["stats_v3"]   = stats_cache
            save_cache(cache)

    cache["player_ids"] = id_cache
    cache["stats_v3"]   = stats_cache
    save_cache(cache)

    # ── Aggiungi colonne al dataframe ──────────────────────────────────────────
    df_stats = pd.DataFrame(results).reset_index(drop=True)

    STATS_COLS = {
        "rating":                   "sofascore_rating",
        "goals":                    "goals_sofascore",
        "assists":                  "assists_sofascore",
        "accuratePasses":           "accurate_passes",
        "accuratePassesPercentage": "pass_completion_pct",
        "accurateLongBalls":        "accurate_long_balls",
        "accurateCrosses":          "accurate_crosses",
        "keyPasses":                "key_passes",
        "bigChancesCreated":        "big_chances_created",
        "bigChancesMissed":         "big_chances_missed",
        "successfulDribbles":       "successful_dribbles",
        "tackles":                  "tackles_sofascore",
        "interceptions":            "interceptions_sofascore",
        "blockedShots":             "blocked_shots",
        "aerialDuelsWon":           "aerial_duels_won",
        "totalShots":               "total_shots",
        "shotsOnTarget":            "shots_on_target_sofascore",
        "shotsFromInsideTheBox":    "shots_inside_box",
        "expectedGoals":            "xG",
        "expectedAssists":          "xA",
        "minutesPlayed":            "minutes_sofascore",
        "appearances":              "appearances_sofascore",
        "yellowCards":              "yellow_cards_sofascore",
        "redCards":                 "red_cards_sofascore",
        "dribbledPast":             "dribbled_past",
        "errorLeadToGoal":          "errors_leading_to_goal",
        "totalRating":              "total_rating_sum",
        "countRating":              "count_rating",
    }

    for src, dst in STATS_COLS.items():
        if src in df_stats.columns:
            df[dst] = pd.to_numeric(df_stats[src], errors="coerce")
        else:
            df[dst] = np.nan

    final = df["sofascore_rating"].notna().sum()
    print(f"\n✅ Stats scaricate: {final}/{len(df)} giocatori")
    print(f"   ❌ Non trovati: {missing}")

    df.to_csv(ENRICHED_PATH, index=False)
    print(f"\n💾 Salvato: {ENRICHED_PATH}")
    print(f"   {len(df)} righe × {len(df.columns)} colonne")
    print("\n🎉 Enrichment completato!")

if __name__ == "__main__":
    main()