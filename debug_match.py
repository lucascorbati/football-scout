import pandas as pd
import json
import unicodedata
from thefuzz import process

def normalize(s: str) -> str:
    s = s.lower().strip()
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return s

with open("data/sofascore_cache.json", encoding="utf-8") as f:
    cache = json.load(f)

player_map = cache.get("player_map", {})

# Mappa normalizzata
normalized_map = {}
for key in player_map:
    pname, tname = key.split("|", 1)
    norm_key = f"{normalize(pname)}|{normalize(tname)}"
    normalized_map[norm_key] = key

# Mappa per squadra: {squadra_norm: [nome_giocatore_norm, ...]}
team_players = {}
for norm_key in normalized_map:
    pname, tname = norm_key.split("|", 1)
    if tname not in team_players:
        team_players[tname] = []
    team_players[tname].append(pname)

TEAM_NAME_MAP = {
    "liverpool":           "liverpool fc",
    "manchester utd":      "manchester united",
    "brighton":            "brighton & hove albion",
    "wolves":              "wolverhampton",
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
    "leverkusen":          "bayer 04 leverkusen",
    "gladbach":            "borussia m'gladbach",
    "freiburg":            "sc freiburg",
    "wolfsburg":           "vfl wolfsburg",
    "hoffenheim":          "tsg hoffenheim",
    "augsburg":            "fc augsburg",
    "mainz 05":            "1. fsv mainz 05",
    "koln":                "1. fc koln",
    "union berlin":        "1. fc union berlin",
    "heidenheim":          "1. fc heidenheim",
    "st pauli":            "fc st. pauli",
    "stuttgart":           "vfb stuttgart",
    "werder bremen":       "sv werder bremen",
    "rb leipzig":          "rb leipzig",
    "eintracht frankfurt": "eintracht frankfurt",
    "hamburger sv":        "hamburger sv",
    "bayern munich":       "fc bayern munchen",
    "marseille":           "olympique de marseille",
    "lyon":                "olympique lyonnais",
    "monaco":              "as monaco",
    "lens":                "rc lens",
    "strasbourg":          "rc strasbourg",
    "rennes":              "stade rennais",
    "brest":               "stade brestois",
}

df = pd.read_csv("output/players_cleaned.csv")

matched        = 0
fuzzy_matched  = 0
unmatched      = []
fuzzy_map      = {}  # CSV key → cache key (per uso in enrich)

for _, row in df.iterrows():
    pname        = str(row["player"]).lower().strip()
    tname        = str(row["team"]).lower().strip()
    tname_mapped = TEAM_NAME_MAP.get(normalize(tname), normalize(tname))
    norm_key     = f"{normalize(pname)}|{normalize(tname_mapped)}"

    # Match esatto
    if norm_key in normalized_map:
        matched += 1
        continue

    # Fuzzy match solo sulla stessa squadra
    squad_players = team_players.get(normalize(tname_mapped), [])
    if squad_players:
        result = process.extractOne(normalize(pname), squad_players, score_cutoff=85)
        if result:
            fuzzy_key = f"{result[0]}|{normalize(tname_mapped)}"
            if fuzzy_key in normalized_map:
                fuzzy_matched += 1
                fuzzy_map[norm_key] = normalized_map[fuzzy_key]
                continue

    unmatched.append((pname, tname, tname_mapped))

print(f"✅ Match esatto:  {matched}/{len(df)}")
print(f"🔍 Match fuzzy:   {fuzzy_matched}/{len(df)}")
print(f"📊 Totale match:  {matched + fuzzy_matched}/{len(df)}")
print(f"❌ Non matchati:  {len(unmatched)}")
print(f"\nPrimi 20 non matchati:")
for p, t, tm in unmatched[:20]:
    print(f"  '{p}' | '{t}' → '{tm}'")

# Salva fuzzy_map per uso in enrich
with open("data/fuzzy_map.json", "w", encoding="utf-8") as f:
    json.dump(fuzzy_map, f, ensure_ascii=False, indent=2)
print(f"\n💾 Fuzzy map salvata: {len(fuzzy_map)} entry")