# Football Scout — Recommendation System

**Data Mining and Text Analytics Project**
IULM University — A.A. 2025/2026

---

## Descrizione del Progetto

Football Scout è un sistema di raccomandazione per calciatori dei top 5 campionati europei (stagione 2025/26). Dato il nome di un calciatore, il sistema restituisce una lista di giocatori simili per statistiche e stile di gioco, utilizzando tecniche di cosine similarity con pesi differenziati per ruolo.

### Funzionalità principali
- Giocatori Simili — top 15 calciatori più simili per statistiche avanzate
- Calciomercato — profili giovani (max 24 anni) ed esperti (26-32 anni)
- Confronto Diretto — confronto statistico tra due giocatori
- Ricerca insensibile ad accenti e varianti del nome
- Filtri per campionato, fascia d'età e minutaggio minimo

### Campionati coperti
- Premier League
- La Liga
- Serie A
- Bundesliga
- Ligue 1

---

## Struttura del Progetto

- data/ — dataset originale FBref
- output/ — dataset pulito e arricchito
- clean_dataset.py — pulizia e normalizzazione dataset
- enrich_dataset.py — arricchimento via Sofascore API
- rematch_missing.py — recupero giocatori non matchati
- recommendation_system.py — app principale Streamlit
- requirements.txt — librerie necessarie

---

## Installazione e Avvio

### 1. Clona il repository

    git clone https://github.com/lucascorbati/football-scout.git
    cd football-scout

### 2. Crea e attiva l'ambiente Conda

    conda create -n football_scout python=3.11 -y
    conda activate football_scout

### 3. Installa le dipendenze

    pip install -r requirements.txt

### 4. Avvia l'applicazione

    streamlit run recommendation_system.py

---

## Metodologia

Il sistema utilizza Cosine Similarity su vettori di statistiche normalizzate con MinMaxScaler. Le metriche vengono pesate in base al ruolo del giocatore con pesi da 1 a 5.

| Ruolo | Priorità principale |
|-------|-------------------|
| Portiere (GK) | Clean sheet, parate, gol subiti |
| Difensore Centrale (CB) | Tackle, intercetti, duelli aerei |
| Terzino (FB) | Cross, intercetti, dribbling subiti |
| Mediano (DM) | Passaggi, recuperi, tackle |
| Centrocampista (CM) | Gol, assist, passaggi chiave |
| Trequartista/Ala (AM) | Gol, assist, dribbling, xG, xA |
| Punta (FW) | Gol, tiri, xG, xA, big chances |

---

## Dati

- Fonte primaria: FBref — dataset stagione 2025/26
- Fonte secondaria: Sofascore API via RapidAPI
- Giocatori nel dataset: circa 2.477 con statistiche complete
- Metriche utilizzate: 32 statistiche avanzate per giocatore

---

## Tecnologie Utilizzate

- Python 3.11
- Streamlit — interfaccia web
- Pandas e NumPy — manipolazione dati
- Scikit-learn — normalizzazione e cosine similarity
- Requests — chiamate API
- TheFuzz — fuzzy matching nomi giocatori
