"""
clean_dataset.py
----------------
Pulizia e deduplicazione del dataset players_data-2025_2026.csv.

Output:
  - output/players_cleaned.csv       → tutti i giocatori di movimento
  - output/goalkeepers_cleaned.csv   → solo portieri
"""

import pandas as pd
import numpy as np
import os

# ── Paths ──────────────────────────────────────────────────────────────────────
INPUT   = os.path.join("data", "players_data-2025_2026.csv")
OUT_DIR = "output"
os.makedirs(OUT_DIR, exist_ok=True)

# ── 1. Caricamento ─────────────────────────────────────────────────────────────
print("📥 Caricamento dataset...")
df = pd.read_csv(INPUT)
print(f"   Shape originale: {df.shape[0]} righe × {df.shape[1]} colonne\n")

# ── 2. Rimozione colonne duplicate/ridondanti ──────────────────────────────────
REDUNDANT_SUFFIXES = [
    "Rk_stats_keeper", "Nation_stats_keeper", "Pos_stats_keeper",
    "Comp_stats_keeper", "Age_stats_keeper", "Born_stats_keeper",
    "MP_stats_keeper", "Starts_stats_keeper", "Min_stats_keeper",
    "90s_stats_keeper", "PKatt_stats_keeper",
    "Rk_stats_shooting", "Nation_stats_shooting", "Pos_stats_shooting",
    "Comp_stats_shooting", "Age_stats_shooting", "Born_stats_shooting",
    "90s_stats_shooting", "Gls_stats_shooting", "PK_stats_shooting",
    "PKatt_stats_shooting",
    "Rk_stats_playing_time", "Nation_stats_playing_time", "Pos_stats_playing_time",
    "Comp_stats_playing_time", "Age_stats_playing_time", "Born_stats_playing_time",
    "MP_stats_playing_time", "Min_stats_playing_time", "90s_stats_playing_time",
    "Starts_stats_playing_time",
    "Rk_stats_misc", "Nation_stats_misc", "Pos_stats_misc",
    "Comp_stats_misc", "Age_stats_misc", "Born_stats_misc",
    "90s_stats_misc", "CrdY_stats_misc", "CrdR_stats_misc",
]

cols_to_drop = [c for c in REDUNDANT_SUFFIXES if c in df.columns]
df.drop(columns=cols_to_drop, inplace=True)
print(f"🗑️  Rimosse {len(cols_to_drop)} colonne ridondanti")

# ── 3. Rinomina colonne ────────────────────────────────────────────────────────
RENAME_MAP = {
    "Rk": "rank", "Player": "player", "Nation": "nation",
    "Pos": "position", "Squad": "team", "Comp": "league",
    "Age": "age", "Born": "birth_year",
    "MP": "matches_played", "Starts": "starts",
    "Min": "minutes", "90s": "nineties_played",
    "Gls": "goals", "Ast": "assists", "G+A": "goals_assists",
    "G-PK": "goals_no_pk", "PK": "penalties_scored",
    "PKatt": "penalties_attempted", "G+A-PK": "goals_assists_no_pk",
    "CrdY": "yellow_cards", "CrdR": "red_cards", "2CrdY": "second_yellow",
    "GA": "gk_goals_against", "GA90": "gk_goals_against_90",
    "SoTA": "gk_shots_on_target_against", "Saves": "gk_saves",
    "Save%": "gk_save_pct", "W": "gk_wins", "D": "gk_draws",
    "L": "gk_losses", "CS": "gk_clean_sheets", "CS%": "gk_clean_sheet_pct",
    "PKA": "gk_pk_against", "PKsv": "gk_pk_saved", "PKm": "gk_pk_missed",
    "Sh": "shots", "SoT": "shots_on_target", "SoT%": "shots_on_target_pct",
    "Sh/90": "shots_per_90", "SoT/90": "shots_on_target_per_90",
    "G/Sh": "goals_per_shot", "G/SoT": "goals_per_shot_on_target",
    "Mn/MP": "minutes_per_match", "Min%": "minutes_pct",
    "Mn/Start": "minutes_per_start", "Compl": "complete_matches",
    "Subs": "substitutions_in", "Mn/Sub": "minutes_per_sub",
    "unSub": "unused_sub", "PPM": "points_per_match",
    "onG": "team_goals_on_pitch", "onGA": "team_goals_against_on_pitch",
    "+/-": "goal_diff_on_pitch", "+/-90": "goal_diff_per_90", "On-Off": "on_off",
    "Fls": "fouls_committed", "Fld": "fouls_drawn", "Off": "offsides",
    "Crs": "crosses", "Int": "interceptions", "TklW": "tackles_won", "OG": "own_goals",
}

df.rename(columns={k: v for k, v in RENAME_MAP.items() if k in df.columns}, inplace=True)
print("✏️  Colonne rinominate")

# ── 4. Normalizza league e nation ─────────────────────────────────────────────
df["league"] = df["league"].str.replace(r"^[a-z]{2,3}\s", "", regex=True)
df["nation"] = df["nation"].str.upper().str.strip()
print("🌍 Nazione e campionato normalizzati")

# ── 5. Posizione primaria ─────────────────────────────────────────────────────
df["position_primary"] = df["position"].str.split(",").str[0]
print("⚽ Posizione primaria estratta")

# ── 6. Rimozione duplicati ────────────────────────────────────────────────────
before = len(df)
df.drop_duplicates(subset=["player", "team", "league"], inplace=True)
print(f"🔁 Duplicate rimosse: {before - len(df)} righe")

# ── 7. Conversione tipi numerici ──────────────────────────────────────────────
numeric_cols = [
    "age", "birth_year", "matches_played", "starts", "minutes", "nineties_played",
    "goals", "assists", "goals_assists", "goals_no_pk", "penalties_scored",
    "penalties_attempted", "yellow_cards", "red_cards",
    "shots", "shots_on_target", "shots_on_target_pct", "shots_per_90",
    "shots_on_target_per_90", "goals_per_shot", "goals_per_shot_on_target",
    "minutes_per_match", "minutes_pct", "goal_diff_on_pitch", "goal_diff_per_90",
    "on_off", "fouls_committed", "fouls_drawn", "offsides", "crosses",
    "interceptions", "tackles_won",
    "gk_goals_against", "gk_goals_against_90", "gk_shots_on_target_against",
    "gk_saves", "gk_save_pct", "gk_wins", "gk_draws", "gk_losses",
    "gk_clean_sheets", "gk_clean_sheet_pct", "gk_pk_against",
    "gk_pk_saved", "gk_pk_missed",
]
for col in numeric_cols:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")
print("🔢 Tipi numerici convertiti")

# ── 8. Metriche per 90 minuti ─────────────────────────────────────────────────
eps = 1e-6
nineties = df["nineties_played"].replace(0, eps)
df["goals_per_90"]         = df["goals"] / nineties
df["assists_per_90"]       = df["assists"] / nineties
df["g_a_per_90"]           = df["goals_assists"] / nineties
df["fouls_comm_per_90"]    = df["fouls_committed"] / nineties
df["fouls_drawn_per_90"]   = df["fouls_drawn"] / nineties
df["interceptions_per_90"] = df["interceptions"] / nineties
df["tackles_won_per_90"]   = df["tackles_won"] / nineties
df["crosses_per_90"]       = df["crosses"] / nineties
print("📐 Metriche per 90 minuti calcolate")

# ── 9. Split portieri / giocatori di movimento ────────────────────────────────
gk_mask = df["position_primary"] == "GK"
df_gk   = df[gk_mask].copy()
df_out  = df[~gk_mask].copy()

keeper_stats = [c for c in df_out.columns if c.startswith("gk_")]
df_out.drop(columns=keeper_stats, inplace=True)

print(f"\n✅ Split completato:")
print(f"   Giocatori di movimento : {len(df_out)}")
print(f"   Portieri               : {len(df_gk)}")

# ── 10. Salvataggio ───────────────────────────────────────────────────────────
df_out.to_csv(os.path.join(OUT_DIR, "players_cleaned.csv"), index=False)
df_gk.to_csv(os.path.join(OUT_DIR, "goalkeepers_cleaned.csv"), index=False)

print(f"\n💾 Salvati in output/")
print("🎉 Cleaning completato con successo!")