"""
recommendation_system.py
------------------------
Football Scout — Recommendation System
Tema scuro con accenti arancioni.

Esegui con: streamlit run recommendation_system.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import unicodedata
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics.pairwise import cosine_similarity

# ── Config pagina ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Football Scout",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    /* Sfondo principale */
    .stApp {
        background: linear-gradient(135deg, #0a0a0f 0%, #0d0d15 50%, #0a0a12 100%);
        color: #ffffff;
    }
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #111118 0%, #0e0e16 100%);
        border-right: 1px solid #1e1e2e;
    }
    header[data-testid="stHeader"] { background: transparent; }
    #MainMenu, footer { visibility: hidden; }

    /* Rimuovi bordi rossi */
    *:focus { outline: none !important; box-shadow: none !important; }
    div[data-testid="stSlider"] { border: none !important; }
    div[data-testid="stSlider"] * { border: none !important; }
    [data-baseweb="select"] { border-color: #2a2a3a !important; }
    [data-baseweb="base-input"] { border-color: #2a2a3a !important; }
    .stMultiSelect [data-baseweb="select"] {
        border-color: #2a2a3a !important;
        background: #13131e !important;
    }

    /* Slider */
    div[data-testid="stSlider"] > div > div > div > div {
        background: #ff6b00 !important;
    }
    div[data-testid="stSlider"] > div > div > div {
        background: #1e1e2e !important;
    }

    /* Logo sidebar */
    .sidebar-logo {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 10px 0 20px 0;
        font-size: 20px;
        font-weight: 700;
        color: #ffffff;
    }
    .sidebar-logo span { color: #ff6b00; }

    /* Stat cards */
    .stat-card {
        background: linear-gradient(135deg, #13131e 0%, #17172a 100%);
        border: 1px solid #1e1e30;
        border-radius: 14px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 4px 20px rgba(0,0,0,0.4);
    }
    .stat-card .icon { font-size: 22px; margin-bottom: 6px; }
    .stat-card .value {
        font-size: 28px;
        font-weight: 800;
        color: #ff6b00;
        text-shadow: 0 0 20px rgba(255,107,0,0.3);
    }
    .stat-card .label {
        font-size: 12px;
        color: #666688;
        margin-top: 4px;
    }

    /* Player card */
    .player-card {
        background: linear-gradient(135deg, #13131e 0%, #1a1a28 100%);
        border: 1px solid #2a2a3a;
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.5);
    }
    .player-name {
        font-size: 32px;
        font-weight: 800;
        color: #ffffff;
        margin-bottom: 4px;
    }
    .player-info { font-size: 15px; color: #8888aa; margin-bottom: 12px; }
    .role-badge {
        display: inline-block;
        background: linear-gradient(135deg, #ff6b00, #ff8c00);
        color: #ffffff;
        font-size: 12px;
        font-weight: 600;
        padding: 4px 14px;
        border-radius: 20px;
        box-shadow: 0 2px 10px rgba(255,107,0,0.4);
    }

    /* Best match card */
    .best-match-card {
        background: linear-gradient(135deg, #13131e 0%, #1a1a28 100%);
        border: 1px solid #ff6b0066;
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 8px 32px rgba(255,107,0,0.1);
    }
    .best-match-label {
        font-size: 11px;
        font-weight: 700;
        color: #ff6b00;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        margin-bottom: 8px;
    }
    .best-match-name {
        font-size: 26px;
        font-weight: 800;
        color: #ffffff;
        margin-bottom: 4px;
    }
    .best-match-info { font-size: 14px; color: #8888aa; }

    /* Score */
    .score-circle { text-align: center; padding: 10px; }
    .score-value {
        font-size: 52px;
        font-weight: 900;
        color: #ff6b00;
        line-height: 1;
        text-shadow: 0 0 30px rgba(255,107,0,0.5);
    }
    .score-label { font-size: 13px; color: #8888aa; margin-top: 4px; }

    /* Category bars */
    .category-bar-container { margin-bottom: 10px; }
    .category-bar-label {
        display: flex;
        justify-content: space-between;
        font-size: 13px;
        color: #ccccdd;
        margin-bottom: 4px;
    }
    .category-bar-bg {
        background: #1e1e2e;
        border-radius: 4px;
        height: 6px;
        width: 100%;
    }
    .category-bar-fill {
        background: linear-gradient(90deg, #ff6b00, #ff8c00);
        border-radius: 4px;
        height: 6px;
        box-shadow: 0 0 8px rgba(255,107,0,0.4);
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background: transparent;
        border-bottom: 1px solid #1e1e2e;
        gap: 0;
    }
    .stTabs [data-baseweb="tab"] {
        background: transparent !important;
        color: #8888aa;
        font-size: 15px;
        font-weight: 600;
        padding: 12px 24px;
        border: none !important;
        outline: none !important;
    }
    .stTabs [aria-selected="true"] {
        background: transparent !important;
        color: #ff6b00 !important;
        border-bottom: 2px solid #ff6b00 !important;
    }

    /* Result rows */
    .result-row {
        background: linear-gradient(135deg, #13131e 0%, #17172a 100%);
        border: 1px solid #1e1e2e;
        border-radius: 10px;
        padding: 14px 16px;
        margin-bottom: 8px;
        display: flex;
        align-items: center;
        gap: 16px;
        transition: border-color 0.2s, transform 0.1s;
    }
    .result-row:hover {
        border-color: #ff6b0044;
        transform: translateX(2px);
    }
    .result-rank {
        font-size: 16px;
        font-weight: 700;
        color: #555566;
        width: 24px;
        text-align: center;
    }
    .result-name { font-size: 15px; font-weight: 600; color: #ffffff; flex: 2; }
    .result-team { font-size: 13px; color: #8888aa; flex: 2; }
    .result-stat { font-size: 13px; color: #ccccdd; flex: 1; text-align: center; }
    .result-similarity { font-size: 15px; font-weight: 700; flex: 1; text-align: right; }

    /* Dataframe */
    div[data-testid="stDataFrame"] {
        border-radius: 12px;
        border: 1px solid #1e1e2e !important;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
    }

    /* Metrics */
    div[data-testid="metric-container"] {
        background: linear-gradient(135deg, #13131e, #17172a);
        border: 1px solid #1e1e2e;
        border-radius: 12px;
        padding: 16px;
        box-shadow: 0 4px 16px rgba(0,0,0,0.3);
    }
    div[data-testid="metric-container"] label {
        color: #8888aa !important;
        font-size: 12px !important;
    }
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-size: 20px !important;
        font-weight: 700 !important;
    }

    /* Input */
    div[data-testid="stTextInput"] input {
        background: #13131e !important;
        border: 1px solid #2a2a3a !important;
        color: #ffffff !important;
        border-radius: 8px !important;
    }
    div[data-testid="stTextInput"] input:focus {
        border-color: #ff6b00 !important;
        box-shadow: 0 0 0 1px #ff6b0066 !important;
    }

    /* Section label */
    .section-label {
        font-size: 11px;
        font-weight: 700;
        color: #ff6b00;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        margin-bottom: 12px;
        margin-top: 20px;
    }

    /* Info footer */
    .info-footer {
        font-size: 12px;
        color: #333344;
        margin-top: 16px;
        padding-top: 12px;
        border-top: 1px solid #1e1e2e;
    }

    /* Divider */
    hr { border-color: #1e1e2e !important; }

    /* Scrollbar */
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: #0a0a0f; }
    ::-webkit-scrollbar-thumb {
        background: #ff6b0066;
        border-radius: 3px;
    }
    ::-webkit-scrollbar-thumb:hover { background: #ff6b00; }
</style>
""", unsafe_allow_html=True)

# ── Caricamento dataset ────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("output/players_enriched.csv")
    df = df[df["minutes"].fillna(0) >= 300].copy()
    df = df.reset_index(drop=True)
    return df

# ── Normalizzazione nomi ───────────────────────────────────────────────────────
def normalize_name(s: str) -> str:
    s = s.lower().strip()
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return s

# ── Mapping ruoli ──────────────────────────────────────────────────────────────
def get_macro_role(pos: str) -> str:
    pos = str(pos).upper().strip()
    if "GK" in pos:                               return "GK"
    elif any(p in pos for p in ["CB", "DC"]):     return "CB"
    elif any(p in pos for p in ["LB","RB","WB"]): return "FB"
    elif "DM" in pos:                             return "DM"
    elif "CM" in pos:                             return "CM"
    elif any(p in pos for p in ["AM","LW","RW"]): return "AM"
    elif "FW" in pos:                             return "FW"
    else:                                          return "CM"

def get_role_label(pos: str) -> str:
    m = get_macro_role(pos)
    return {
        "GK":"Portiere","CB":"Difensore Centrale","FB":"Terzino",
        "DM":"Mediano","CM":"Centrocampista","AM":"Trequartista/Ala","FW":"Punta"
    }.get(m, "Centrocampista")

# ── Gruppi ruoli ───────────────────────────────────────────────────────────────
ROLE_GROUPS = {
    "GK": ["GK"],
    "CB": ["CB", "DC"],
    "FB": ["LB", "RB", "WB"],
    "DM": ["DM", "CM"],
    "CM": ["CM", "DM"],
    "AM": ["AM", "LW", "RW"],
    "FW": ["FW"],
}

# ── Pesi per ruolo ─────────────────────────────────────────────────────────────
WEIGHTS = {
    "GK": {
        "matches_played":5,"starts":5,"minutes":5,"nineties_played":5,
        "gk_goals_against":5,"gk_goals_against_90":5,
        "gk_shots_on_target_against":5,"gk_saves":5,"gk_save_pct":5,
        "gk_clean_sheets":5,"gk_clean_sheet_pct":5,
        "gk_wins":5,"gk_draws":5,"gk_losses":5,
        "gk_pk_against":5,"gk_pk_saved":5,
        "accurate_passes":3,"pass_completion_pct":3,"accurate_long_balls":3,
        "yellow_cards":5,"red_cards":5,
    },
    "CB": {
        "matches_played":5,"starts":5,"minutes":5,"nineties_played":5,
        "goals":3.5,"assists":3.5,"goals_assists":4,
        "penalties_scored":2,"penalties_attempted":2,
        "shots":1,"shots_on_target":1,"shots_on_target_pct":1,
        "shots_per_90":1,"goals_per_shot":1,"total_shots":1,
        "shots_on_target_sofascore":1,"shots_inside_box":1,
        "accurate_passes":3,"pass_completion_pct":3,
        "accurate_long_balls":4,"accurate_crosses":4,"key_passes":2,
        "successful_dribbles":1,"dribbled_past":5,
        "tackles_sofascore":5,"interceptions_sofascore":5,
        "blocked_shots":5,"aerial_duels_won":5,
        "fouls_committed":5,"fouls_drawn":5,"tackles_won":5,"interceptions":5,
        "sofascore_rating":3,
        "yellow_cards":5,"red_cards":5,"yellow_cards_sofascore":5,
        "red_cards_sofascore":5,"errors_leading_to_goal":5,
    },
    "FB": {
        "matches_played":5,"starts":5,"minutes":5,"nineties_played":5,
        "goals":3.5,"assists":3.5,"goals_assists":4,
        "penalties_scored":2,"penalties_attempted":2,
        "shots":1,"shots_on_target":1,"shots_on_target_pct":1,
        "shots_per_90":1,"goals_per_shot":1,"total_shots":1,
        "shots_on_target_sofascore":1,"shots_inside_box":1,
        "accurate_passes":3,"pass_completion_pct":3,
        "accurate_long_balls":4,"accurate_crosses":4,"key_passes":2,
        "successful_dribbles":1,"dribbled_past":5,
        "tackles_sofascore":5,"interceptions_sofascore":5,
        "blocked_shots":5,"aerial_duels_won":5,
        "fouls_committed":5,"fouls_drawn":5,"tackles_won":5,"interceptions":5,
        "sofascore_rating":3,
        "yellow_cards":5,"red_cards":5,"yellow_cards_sofascore":5,
        "red_cards_sofascore":5,"errors_leading_to_goal":5,
    },
    "DM": {
        "matches_played":5,"starts":5,"minutes":5,"nineties_played":5,
        "goals":5,"assists":5,"goals_assists":5,
        "penalties_scored":5,"penalties_attempted":5,
        "goals_no_pk":3,"goals_per_90":3,"assists_per_90":3,"g_a_per_90":3,
        "shots":3,"shots_on_target":3,"shots_on_target_pct":3,
        "shots_per_90":3,"goals_per_shot":3,"total_shots":3,
        "shots_on_target_sofascore":3,"shots_inside_box":3,
        "accurate_passes":5,"pass_completion_pct":5,
        "accurate_long_balls":5,"accurate_crosses":5,
        "key_passes":5,"big_chances_created":5,
        "successful_dribbles":5,"dribbled_past":5,"big_chances_missed":5,
        "tackles_sofascore":4,"interceptions_sofascore":4,
        "blocked_shots":4,"aerial_duels_won":4,
        "fouls_committed":4,"fouls_drawn":4,"tackles_won":4,"interceptions":4,
        "xG":2,"xA":2,"sofascore_rating":3,"total_rating_sum":2,"count_rating":2,
        "yellow_cards":5,"red_cards":5,"errors_leading_to_goal":5,
    },
    "CM": {
        "matches_played":5,"starts":5,"minutes":5,"nineties_played":5,
        "goals":5,"assists":5,"goals_assists":5,
        "penalties_scored":5,"penalties_attempted":5,
        "goals_no_pk":3,"goals_per_90":3,"assists_per_90":3,"g_a_per_90":3,
        "shots":3,"shots_on_target":3,"shots_on_target_pct":3,
        "shots_per_90":3,"goals_per_shot":3,"total_shots":3,
        "shots_on_target_sofascore":3,"shots_inside_box":3,
        "accurate_passes":5,"pass_completion_pct":5,
        "accurate_long_balls":5,"accurate_crosses":5,
        "key_passes":5,"big_chances_created":5,
        "successful_dribbles":5,"dribbled_past":5,"big_chances_missed":5,
        "tackles_sofascore":4,"interceptions_sofascore":4,
        "blocked_shots":4,"aerial_duels_won":4,
        "fouls_committed":4,"fouls_drawn":4,"tackles_won":4,"interceptions":4,
        "xG":2,"xA":2,"sofascore_rating":3,"total_rating_sum":2,"count_rating":2,
        "yellow_cards":5,"red_cards":5,"errors_leading_to_goal":5,
    },
    "AM": {
        "matches_played":5,"starts":5,"minutes":5,"nineties_played":5,
        "goals":5,"assists":5,"goals_assists":5,
        "goals_no_pk":5,"goals_per_90":5,"assists_per_90":5,"g_a_per_90":5,
        "penalties_scored":5,"penalties_attempted":5,
        "goals_sofascore":5,"assists_sofascore":5,
        "shots":5,"shots_on_target":5,"shots_on_target_pct":5,
        "shots_per_90":5,"goals_per_shot":5,"total_shots":5,
        "shots_on_target_sofascore":5,"shots_inside_box":5,
        "accurate_passes":4,"pass_completion_pct":4,
        "accurate_long_balls":3,"accurate_crosses":4,
        "key_passes":4,"big_chances_created":4,
        "successful_dribbles":5,"dribbled_past":5,"big_chances_missed":5,
        "tackles_sofascore":2,"interceptions_sofascore":2,
        "blocked_shots":2,"aerial_duels_won":4,
        "fouls_committed":2,"fouls_drawn":2,"tackles_won":2,"interceptions":2,
        "xG":5,"xA":5,"sofascore_rating":3,
        "yellow_cards":2,"red_cards":2,"yellow_cards_sofascore":2,
        "red_cards_sofascore":2,"errors_leading_to_goal":2,
    },
    "FW": {
        "matches_played":5,"starts":5,"minutes":5,"nineties_played":5,
        "goals":5,"assists":5,"goals_assists":5,
        "goals_no_pk":5,"goals_per_90":5,"assists_per_90":5,"g_a_per_90":5,
        "penalties_scored":5,"penalties_attempted":5,
        "goals_sofascore":5,"assists_sofascore":5,
        "shots":5,"shots_on_target":5,"shots_on_target_pct":5,
        "shots_per_90":5,"goals_per_shot":5,"total_shots":5,
        "shots_on_target_sofascore":5,"shots_inside_box":5,
        "accurate_passes":4,"pass_completion_pct":4,
        "accurate_long_balls":3,"accurate_crosses":4,
        "key_passes":4,"big_chances_created":4,
        "successful_dribbles":5,"dribbled_past":5,"big_chances_missed":5,
        "tackles_sofascore":2,"interceptions_sofascore":2,
        "blocked_shots":2,"aerial_duels_won":4,
        "fouls_committed":2,"fouls_drawn":2,"tackles_won":2,"interceptions":2,
        "xG":5,"xA":5,"sofascore_rating":3,
        "yellow_cards":2,"red_cards":2,"yellow_cards_sofascore":2,
        "red_cards_sofascore":2,"errors_leading_to_goal":2,
    },
}

# ── Categorie per barre ────────────────────────────────────────────────────────
CATEGORY_COLS = {
    "Attacco":      ["goals","assists","goals_assists","xG","xA","goals_sofascore"],
    "Passaggi":     ["accurate_passes","pass_completion_pct","key_passes","big_chances_created"],
    "Difesa":       ["tackles_sofascore","interceptions_sofascore","aerial_duels_won","blocked_shots"],
    "Progressione": ["successful_dribbles","shots_per_90","shots_inside_box"],
    "Fisico":       ["minutes","matches_played","aerial_duels_won","fouls_drawn"],
}

def compute_category_scores(player: pd.Series, df: pd.DataFrame) -> dict:
    scores = {}
    for cat, cols in CATEGORY_COLS.items():
        avail = [c for c in cols if c in df.columns]
        if not avail:
            scores[cat] = 0
            continue
        vals   = df[avail].fillna(0)
        scaler = MinMaxScaler()
        scaled = scaler.fit_transform(vals)
        try:
            p_scaled = scaled[df.index.get_loc(player.name)]
        except:
            p_scaled = scaled[0]
        scores[cat] = int(round(p_scaled.mean() * 100))
    return scores

# ── Età ────────────────────────────────────────────────────────────────────────
def age_similarity(age1: float, age2: float) -> float:
    return max(0.0, 1.0 - abs(age1 - age2) / 10.0)

# ── Calcolo similarità ─────────────────────────────────────────────────────────
def compute_similarity(df: pd.DataFrame, player_idx: int,
                       role: str, top_n: int = 20,
                       age_filter: str = "tutti",
                       player_age: float = 25.0) -> pd.DataFrame:

    weights        = WEIGHTS.get(role, WEIGHTS["CM"])
    available_cols = [c for c in weights.keys() if c in df.columns]

    feat_df       = df[available_cols].fillna(0).copy()
    scaler        = MinMaxScaler()
    feat_scaled   = scaler.fit_transform(feat_df)
    weight_vector = np.array([weights[c] for c in available_cols])
    feat_weighted = feat_scaled * weight_vector

    player_vec   = feat_weighted[player_idx].reshape(1, -1)
    similarities = cosine_similarity(player_vec, feat_weighted)[0]

    age_sims = df["age"].fillna(25).apply(
        lambda a: age_similarity(player_age, a)
    ).values

    if age_filter == "giovani":
        age_bonus    = df["age"].fillna(25).apply(
            lambda a: 1.0 if a <= 24 else 0.0
        ).values
        final_scores = 0.75 * similarities + 0.05 * age_sims + 0.20 * age_bonus
    elif age_filter == "esperti":
        age_bonus    = df["age"].fillna(25).apply(
            lambda a: 1.0 if 26 <= a <= 32 else 0.3
        ).values
        final_scores = 0.75 * similarities + 0.05 * age_sims + 0.20 * age_bonus
    else:
        final_scores = similarities

    # Filtro ruolo preciso
    player_pos   = str(df.iloc[player_idx]["position_primary"]).upper().strip()
    player_macro = get_macro_role(player_pos)
    player_group = []
    for gk, gv in ROLE_GROUPS.items():
        if any(p in player_pos for p in gv):
            player_group = gv
            break
    if not player_group:
        player_group = [player_pos]

    result_df = df.copy()
    result_df["similarity_score"] = final_scores
    result_df = result_df[result_df.index != player_idx]
    result_df["_macro"] = result_df["position_primary"].apply(get_macro_role)
    result_df["_pos"]   = result_df["position_primary"].str.upper().str.strip()

    strict = result_df[result_df["_pos"].apply(
        lambda p: any(g in p for g in player_group)
    )]
    if len(strict) >= top_n:
        result_df = strict
    else:
        result_df = result_df[result_df["_macro"] == player_macro]

    result_df = result_df.sort_values("similarity_score", ascending=False).head(top_n)
    result_df["similarity_pct"] = (result_df["similarity_score"] * 100).round(1)
    return result_df

# ── Colonne dettaglio ──────────────────────────────────────────────────────────
DETAIL_COLS = [
    "matches_played","starts","minutes","goals","assists","goals_assists",
    "goals_no_pk","goals_per_90","assists_per_90","shots","shots_on_target",
    "shots_on_target_pct","xG","xA","accurate_passes","pass_completion_pct",
    "accurate_long_balls","accurate_crosses","key_passes","big_chances_created",
    "successful_dribbles","dribbled_past","tackles_sofascore",
    "interceptions_sofascore","blocked_shots","aerial_duels_won",
    "fouls_committed","fouls_drawn","sofascore_rating",
    "yellow_cards","red_cards","errors_leading_to_goal"
]

# ── HTML helpers ───────────────────────────────────────────────────────────────
def render_category_bars(scores: dict) -> str:
    html = ""
    for cat, val in scores.items():
        html += f"""
        <div class="category-bar-container">
            <div class="category-bar-label">
                <span>{cat}</span>
                <span style="color:#ff6b00;font-weight:700">{val}</span>
            </div>
            <div class="category-bar-bg">
                <div class="category-bar-fill" style="width:{val}%"></div>
            </div>
        </div>"""
    return html

def render_results_table(recs: pd.DataFrame) -> str:
    html = """
    <div style="margin-top:16px">
    <div style="display:flex;align-items:center;gap:16px;padding:8px 16px;
                font-size:11px;color:#555566;font-weight:700;
                letter-spacing:1px;text-transform:uppercase;margin-bottom:4px">
        <span style="width:24px">#</span>
        <span style="flex:2">Giocatore</span>
        <span style="flex:2">Squadra · Campionato</span>
        <span style="flex:1;text-align:center">Ruolo</span>
        <span style="flex:1;text-align:center">Età</span>
        <span style="flex:1;text-align:center">Gol</span>
        <span style="flex:1;text-align:center">Assist</span>
        <span style="flex:1;text-align:center">xG</span>
        <span style="flex:1;text-align:center">xA</span>
        <span style="flex:1;text-align:center">Rating</span>
        <span style="flex:1;text-align:right">Similarità</span>
    </div>"""

    for i, (_, row) in enumerate(recs.iterrows()):
        sim     = row.get("similarity_pct", 0)
        goals   = int(row.get("goals", 0) or 0)
        assists = int(row.get("assists", 0) or 0)
        xg      = round(float(row.get("xG", 0) or 0), 2)
        xa      = round(float(row.get("xA", 0) or 0), 2)
        rating  = round(float(row.get("sofascore_rating", 0) or 0), 2)
        age     = int(row.get("age", 0) or 0)
        pos     = row.get("position_primary", "N/A")
        color   = "#00cc66" if sim >= 90 else "#ff6b00" if sim >= 75 else "#ffaa00"

        html += f"""
        <div class="result-row">
            <span class="result-rank">{i+1}</span>
            <span class="result-name">{row.get('player','')}</span>
            <span class="result-team">{row.get('team','')} · {row.get('league','')}</span>
            <span class="result-stat">{pos}</span>
            <span class="result-stat">{age}</span>
            <span class="result-stat">{goals}</span>
            <span class="result-stat">{assists}</span>
            <span class="result-stat">{xg}</span>
            <span class="result-stat">{xa}</span>
            <span class="result-stat">{rating}</span>
            <span class="result-similarity" style="color:{color}">{sim}%</span>
        </div>"""

    html += f"""
    <div class="info-footer">
        ℹ️ I punteggi di similarità sono calcolati su {len(DETAIL_COLS)} metriche e pesati per importanza.
    </div></div>"""
    return html

# ── Main ───────────────────────────────────────────────────────────────────────
def main():
    df = load_data()
    df["_name_norm"] = df["player"].apply(normalize_name)

    # ── Sidebar ────────────────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown("""
        <div class="sidebar-logo">⚽ Football <span>Scout</span></div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="section-label">Cerca Giocatore</div>',
                    unsafe_allow_html=True)
        search_input = st.text_input(
            "", placeholder="🔍 Cerca un giocatore...",
            label_visibility="collapsed"
        )

        st.markdown('<div class="section-label">Filtri Raccomandazioni</div>',
                    unsafe_allow_html=True)
        st.markdown("**Campionato**")
        all_leagues   = sorted(df["league"].dropna().unique())
        filter_league = st.multiselect(
            "", options=all_leagues, default=[],
            placeholder="Tutti i campionati",
            label_visibility="collapsed"
        )
        st.markdown("**Fascia d'età**")
        filter_age_min, filter_age_max = st.slider(
            "", min_value=16, max_value=45,
            value=(16, 45), label_visibility="collapsed"
        )
        st.markdown("**Minuti minimi giocati**")
        min_minutes = st.slider(
            "", min_value=0, max_value=3000,
            value=300, step=100, label_visibility="collapsed"
        )
        st.markdown("**Numero raccomandazioni**")
        top_n = st.slider(
            "", min_value=5, max_value=20,
            value=15, label_visibility="collapsed"
        )

        st.markdown('<div class="section-label">Confronto Diretto</div>',
                    unsafe_allow_html=True)
        compare_input = st.text_input(
            "", placeholder="🔍 Secondo giocatore...",
            label_visibility="collapsed", key="compare"
        )

    # ── Stato vuoto ────────────────────────────────────────────────────────────
    if not search_input:
        c1, c2, c3, c4 = st.columns(4)
        for col, icon, val, label in [
            (c1, "👥", f"{len(df):,}", "Giocatori analizzati"),
            (c2, "🏆", df['league'].nunique(), "Campionati"),
            (c3, "📊", len(DETAIL_COLS), "Metriche utilizzate"),
            (c4, "🕐", "2025/26", "Stagione"),
        ]:
            with col:
                st.markdown(f"""<div class="stat-card">
                    <div class="icon">{icon}</div>
                    <div class="value">{val}</div>
                    <div class="label">{label}</div>
                </div>""", unsafe_allow_html=True)

        st.markdown("""
        <div style="text-align:center;padding:80px 20px;color:#555566">
            <div style="font-size:56px;margin-bottom:16px">⚽</div>
            <div style="font-size:22px;font-weight:600;color:#8888aa;margin-bottom:8px">
                Cerca un giocatore per iniziare
            </div>
            <div style="font-size:14px">
                Inserisci il nome nella barra laterale — supporta accenti e varianti
            </div>
        </div>""", unsafe_allow_html=True)
        return

    # ── Ricerca ────────────────────────────────────────────────────────────────
    search_norm = normalize_name(search_input)
    matches     = df[df["_name_norm"].str.contains(search_norm, na=False)]

    if matches.empty:
        st.error(f"❌ Nessun giocatore trovato per '{search_input}'")
        return

    if len(matches) > 1:
        options    = matches.apply(
            lambda r: f"{r['player']} — {r['team']} ({r['league']})", axis=1
        ).tolist()
        selected   = st.selectbox("Più giocatori trovati:", options)
        player_idx = matches.iloc[options.index(selected)].name
    else:
        player_idx = matches.index[0]

    player     = df.iloc[player_idx]
    role       = get_macro_role(player["position_primary"])
    player_age = float(player.get("age", 25) or 25)

    # ── Stats globali ──────────────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    for col, icon, val, label in [
        (c1, "👥", f"{len(df):,}", "Giocatori analizzati"),
        (c2, "🏆", df['league'].nunique(), "Campionati"),
        (c3, "📊", len(DETAIL_COLS), "Metriche utilizzate"),
        (c4, "🕐", "Oggi", "Aggiornato"),
    ]:
        with col:
            st.markdown(f"""<div class="stat-card">
                <div class="icon">{icon}</div>
                <div class="value">{val}</div>
                <div class="label">{label}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Pool filtrato ──────────────────────────────────────────────────────────
    pool = df.copy()
    if filter_league:
        pool = pool[pool["league"].isin(filter_league)]
    pool = pool[pool["age"].between(filter_age_min, filter_age_max)]
    pool = pool[pool["minutes"].fillna(0) >= min_minutes]
    if player_idx not in pool.index:
        pool = pd.concat([df.iloc[[player_idx]], pool]).drop_duplicates()
    p_loc = pool.index.get_loc(player_idx)

    # ── Calcola raccomandazioni ────────────────────────────────────────────────
    with st.spinner(""):
        recs       = compute_similarity(pool, p_loc, role, top_n,
                                        "tutti", player_age)
        recs_young = compute_similarity(pool, p_loc, role, top_n,
                                        "giovani", player_age)
        recs_exp   = compute_similarity(pool, p_loc, role, top_n,
                                        "esperti", player_age)

    best_match = recs.iloc[0] if len(recs) > 0 else None

    # ── Card giocatore + best match ────────────────────────────────────────────
    col_player, col_best = st.columns([1, 1])

    with col_player:
        st.markdown(f"""
        <div class="player-card">
            <div class="player-name">{player['player']}</div>
            <div class="player-info">
                {player.get('team','N/A')} &bull;
                {player.get('position_primary','N/A')} &bull;
                {int(player_age)} anni &bull;
                🌐 {player.get('nation','N/A')}
            </div>
            <div class="role-badge">{get_role_label(player.get('position_primary',''))}</div>
            <br><br>
            <div style="display:flex;gap:24px;margin-top:8px">
                <div style="text-align:center">
                    <div style="font-size:22px;font-weight:700;color:#ff6b00">
                        {int(player.get('goals',0) or 0)}
                    </div>
                    <div style="font-size:11px;color:#8888aa">Gol</div>
                </div>
                <div style="text-align:center">
                    <div style="font-size:22px;font-weight:700;color:#ff6b00">
                        {int(player.get('assists',0) or 0)}
                    </div>
                    <div style="font-size:11px;color:#8888aa">Assist</div>
                </div>
                <div style="text-align:center">
                    <div style="font-size:22px;font-weight:700;color:#ff6b00">
                        {round(float(player.get('sofascore_rating',0) or 0),2)}
                    </div>
                    <div style="font-size:11px;color:#8888aa">Rating</div>
                </div>
                <div style="text-align:center">
                    <div style="font-size:22px;font-weight:700;color:#ff6b00">
                        {int(player.get('minutes',0) or 0)}
                    </div>
                    <div style="font-size:11px;color:#8888aa">Minuti</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_best:
        if best_match is not None:
            cat_scores = compute_category_scores(player, pool)
            sim_val    = best_match.get("similarity_pct", 0)
            col_info, col_score = st.columns([2, 1])
            with col_info:
                st.markdown(f"""
                <div class="best-match-card">
                    <div class="best-match-label">⚡ Miglior Corrispondenza</div>
                    <div class="best-match-name">{best_match.get('player','')}</div>
                    <div class="best-match-info">
                        {best_match.get('team','')} &rarr; {best_match.get('league','')}
                    </div>
                    <br>
                    {render_category_bars(cat_scores)}
                </div>
                """, unsafe_allow_html=True)
            with col_score:
                st.markdown(f"""
                <div style="display:flex;align-items:center;justify-content:center;
                            height:100%;padding:20px">
                    <div class="score-circle">
                        <div class="score-value">{sim_val}%</div>
                        <div class="score-label">Similarità</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

    # ── Tabs ───────────────────────────────────────────────────────────────────
    tab1, tab2, tab3 = st.tabs([
        "🎯 Giocatori Simili",
        "🛒 Calciomercato",
        "⚔️ Confronto Diretto"
    ])

    # ══ TAB 1 ══════════════════════════════════════════════════════════════════
    with tab1:
        st.markdown(render_results_table(recs), unsafe_allow_html=True)
        st.divider()
        st.markdown('<div class="section-label">Dettaglio e Confronto</div>',
                    unsafe_allow_html=True)
        selected_detail = st.selectbox(
            "Seleziona un giocatore per confrontarlo:",
            recs["player"].tolist(), key="detail_sim"
        )
        if selected_detail:
            detail    = recs[recs["player"] == selected_detail].iloc[0]
            stat_cols = [c for c in DETAIL_COLS if c in df.columns]
            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown(f"**👤 {player['player']}** *(cercato)*")
                st.dataframe(player[stat_cols].to_frame().T,
                             use_container_width=True, hide_index=True)
            with col_b:
                st.markdown(f"**👤 {detail['player']}** — **{detail['similarity_pct']}%**")
                st.dataframe(detail[stat_cols].to_frame().T,
                             use_container_width=True, hide_index=True)
            age2     = float(detail.get("age", 25) or 25)
            age_diff = int(abs(player_age - age2))
            younger  = player["player"] if player_age < age2 else detail["player"]
            st.info(f"📅 Differenza d'età: **{age_diff} anni** — **{younger}** è il più giovane")

    # ══ TAB 2 ══════════════════════════════════════════════════════════════════
    with tab2:
        col_g, col_e = st.columns(2)
        with col_g:
            st.markdown("### 🌱 Profili Giovani *(max 24 anni)*")
            st.markdown(render_results_table(recs_young), unsafe_allow_html=True)
        with col_e:
            st.markdown("### 🏆 Profili Esperti *(26-32 anni)*")
            st.markdown(render_results_table(recs_exp), unsafe_allow_html=True)

        st.divider()
        all_market      = pd.concat([recs_young, recs_exp]).drop_duplicates(subset=["player"])
        selected_market = st.selectbox(
            "Dettaglio profilo:", all_market["player"].tolist(), key="detail_market"
        )
        if selected_market:
            detail_m  = all_market[all_market["player"] == selected_market].iloc[0]
            stat_cols = [c for c in DETAIL_COLS if c in df.columns]
            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown(f"**👤 {player['player']}** *(da sostituire)*")
                st.dataframe(player[stat_cols].to_frame().T,
                             use_container_width=True, hide_index=True)
            with col_b:
                st.markdown(f"**👤 {detail_m['player']}** — **{detail_m['similarity_pct']}%**")
                st.dataframe(detail_m[stat_cols].to_frame().T,
                             use_container_width=True, hide_index=True)

    # ══ TAB 3 ══════════════════════════════════════════════════════════════════
    with tab3:
        if not compare_input:
            st.info("👈 Inserisci il nome del secondo giocatore nella barra laterale.")
        else:
            compare_norm    = normalize_name(compare_input)
            compare_matches = df[df["_name_norm"].str.contains(compare_norm, na=False)]

            if compare_matches.empty:
                st.warning(f"Giocatore '{compare_input}' non trovato.")
            else:
                if len(compare_matches) > 1:
                    opts2 = compare_matches.apply(
                        lambda r: f"{r['player']} — {r['team']} ({r['league']})", axis=1
                    ).tolist()
                    sel2           = st.selectbox("Seleziona:", opts2, key="compare_sel")
                    compare_player = compare_matches.iloc[opts2.index(sel2)]
                else:
                    compare_player = compare_matches.iloc[0]

                age2 = float(compare_player.get("age", 25) or 25)

                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"### 👤 {player['player']}")
                    st.write(f"**Squadra:** {player.get('team','N/A')}")
                    st.write(f"**Campionato:** {player.get('league','N/A')}")
                    st.write(f"**Ruolo:** {get_role_label(player.get('position_primary',''))}")
                    st.write(f"**Età:** {int(player_age)} anni")
                    st.write(f"**Nazione:** {player.get('nation','N/A')}")
                with col2:
                    st.markdown(f"### 👤 {compare_player['player']}")
                    st.write(f"**Squadra:** {compare_player.get('team','N/A')}")
                    st.write(f"**Campionato:** {compare_player.get('league','N/A')}")
                    st.write(f"**Ruolo:** {get_role_label(compare_player.get('position_primary',''))}")
                    st.write(f"**Età:** {int(age2)} anni")
                    st.write(f"**Nazione:** {compare_player.get('nation','N/A')}")

                st.divider()
                stat_cols = [c for c in DETAIL_COLS if c in df.columns]
                comp_df   = pd.DataFrame({
                    player["player"]:         pd.to_numeric(player[stat_cols], errors="coerce"),
                    compare_player["player"]: pd.to_numeric(compare_player[stat_cols], errors="coerce"),
                }).T.round(2)
                st.dataframe(comp_df, use_container_width=True)

                age_diff = int(abs(player_age - age2))
                younger  = player["player"] if player_age < age2 else compare_player["player"]
                older    = player["player"] if player_age > age2 else compare_player["player"]
                st.info(
                    f"📅 **{younger}** è più giovane di **{age_diff} anni** "
                    f"rispetto a **{older}**"
                )

                # Punteggio similarità
                weights = WEIGHTS.get(role, WEIGHTS["CM"])
                avail_w = [c for c in weights.keys() if c in df.columns]
                feat_df     = df[avail_w].fillna(0)
                scaler      = MinMaxScaler()
                feat_scaled = scaler.fit_transform(feat_df)
                w_vec       = np.array([weights[c] for c in avail_w])
                feat_w      = feat_scaled * w_vec
                idx2        = compare_player.name
                sim         = cosine_similarity(
                    feat_w[player_idx].reshape(1,-1),
                    feat_w[idx2].reshape(1,-1)
                )[0][0]
                st.success(f"🎯 **Punteggio di similarità: {sim*100:.1f}%**")

if __name__ == "__main__":
    main()