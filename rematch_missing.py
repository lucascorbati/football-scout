"""
rematch_missing.py
------------------
Secondo passaggio per recuperare i giocatori non matchati.
Strategie:
  1. Ricerca per cognome
  2. Ricerca senza accenti
  3. Ricerca per primo + ultimo nome
  4. Match senza verificare la squadra (primo risultato plausibile)

Output:
  - output/players_enriched.csv (aggiornato)
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

ENRICHED_PATH = os.path.join("output", "players_enriched.csv")
CACHE_FILE    = os.path.join("data",   "sofascore_cache_v3.json")

TOP5_IDS  = {17, 8, 23, 35, 34}

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

# ── API ────────────────────────────────────────────────────────────────────────
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
                print(f"      ⚠️  Errore: {e}")
    return {}

def search_player_advanced(name: str, team: str) -> int | None:
    """Prova più strategie di ricerca."""
    team_norm = normalize(TEAM_NAME_MAP.get(normalize(team), team))
    name_norm = normalize(name)
    parts     = name_norm.split()

    strategies = []

    # 1. Nome completo
    strategies.append(name)

    # 2. Solo cognome (ultima parola)
    if len(parts) > 1:
        strategies.append(parts[-1])

    # 3. Primo + ultimo nome
    if len(parts) > 2:
        strategies.append(f"{parts[0]} {parts[-1]}")

    # 4. Solo primo nome
    strategies.append(parts[0])

    for query in strategies:
        url  = f"{BASE_URL}/players/search?name={requests.utils.quote(query)}"
        data = api_get(url)
        players = data.get("players", [])
        time.sleep(0.3)

        for p in players[:5]:
            p_name = normalize(p.get("name", ""))
            p_team = normalize(p.get("team", {}).get("name", ""))
            pid    = p.get("id")

            # Match con squadra
            if team_norm in p_team and (
                name_norm in p_name or
                all(w in p_name for w in parts)
            ):
                return pid

        # Ultima chance: primo risultato senza verifica squadra
        # solo se il nome corrisponde bene
        if players:
            p      = players[0]
            p_name = normalize(p.get("name", ""))
            pid    = p.get("id")
            if name_norm == p_name or all(w in p_name for w in parts if len(w) > 3):
                return pid

    return None

def get_stats_2526(player_id: int) -> dict:
    url  = f"{BASE_URL}/players/get-all-statistics?playerId={player_id}"
    data = api_get(url)
    seasons = data.get("seasons", [])

    for s in seasons:
        t_id = s.get("uniqueTournament", {}).get("id")
        year = s.get("year", "")
        if t_id not in TOP5_IDS or year != "25/26":
            continue
        stats = s.get("statistics", {})
        if stats:
            return stats
    return {}

# ── Main ───────────────────────────────────────────────────────────────────────
def main():
    print("📥 Caricamento players_enriched.csv...")
    df = pd.read_csv(ENRICHED_PATH)
    df = df.reset_index(drop=True)

    cache       = load_cache()
    id_cache    = cache.get("player_ids", {})
    stats_cache = cache.get("stats_v3",   {})

    # Trova i non matchati
    missing_mask = df["sofascore_rating"].isna()
    missing_df   = df[missing_mask].copy()
    print(f"   Giocatori da recuperare: {len(missing_df)}\n")

    recovered = 0

    for i, (idx, row) in enumerate(missing_df.iterrows()):
        pname = str(row["player"])
        tname = str(row["team"])
        key   = f"{normalize(pname)}|{normalize(tname)}"

        # Prova ricerca avanzata
        pid = search_player_advanced(pname, tname)

        if not pid:
            continue

        # Aggiorna cache ID
        id_cache[key] = pid

        # Scarica stats
        cache_key = str(pid)
        if cache_key in stats_cache and stats_cache[cache_key]:
            stats = stats_cache[cache_key]
        else:
            stats = get_stats_2526(pid)
            stats_cache[cache_key] = stats
            time.sleep(0.4)

        if not stats:
            continue

        # Aggiorna dataframe
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
            if src in stats and dst in df.columns:
                df.at[idx, dst] = stats[src]

        recovered += 1

        if i % 50 == 0 and i > 0:
            print(f"   ... {i}/{len(missing_df)} processati — recuperati: {recovered}")
            cache["player_ids"] = id_cache
            cache["stats_v3"]   = stats_cache
            save_cache(cache)

    cache["player_ids"] = id_cache
    cache["stats_v3"]   = stats_cache
    save_cache(cache)

    # Salva
    df.to_csv(ENRICHED_PATH, index=False)
    final = df["sofascore_rating"].notna().sum()
    print(f"\n✅ Recuperati: {recovered} giocatori aggiuntivi")
    print(f"📊 Totale matchati: {final}/{len(df)}")
    print(f"\n💾 Salvato: {ENRICHED_PATH}")
    print("\n🎉 Rematch completato!")

if __name__ == "__main__":
    main()