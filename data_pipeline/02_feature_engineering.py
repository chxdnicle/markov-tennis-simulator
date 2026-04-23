import pandas as pd
import numpy as np
import json

print("Starting Feature Engineering Pipeline...")

# --- 1. LOAD ALL DATA ---
print("Loading data...")
matches = pd.read_csv("master_match_data.csv")
points = pd.read_csv("master_point_data.csv", low_memory=False)
atp_players = pd.read_csv("atp_players.csv")
wta_players = pd.read_csv("wta_players.csv")

# --- 2. CLEAN PLAYER DATABASE ---
print("Cleaning player data...")
players = pd.concat([atp_players, wta_players], ignore_index=True)
players['name_first'] = players['name_first'].fillna('')
players['name_last'] = players['name_last'].fillna('')
players['full_name'] = (players['name_first'] + " " + players['name_last']).str.strip().str.lower()
players['dob'] = pd.to_datetime(players['dob'].astype(str).str.slice(0, 8), format='%Y%m%d', errors='coerce')
players = players.drop_duplicates(subset=['full_name'])

# --- 3. ENRICH MATCHES (Surface & Age) ---
print("Enriching matches with Age and Surface...")
slam_dates = {'ausopen': '01-15', 'frenchopen': '05-25', 'wimbledon': '07-01', 'usopen': '08-25'}
surface_map = {'ausopen': 'Hard', 'frenchopen': 'Clay', 'wimbledon': 'Grass', 'usopen': 'Hard'}

matches['tourney_date'] = matches.apply(lambda x: pd.to_datetime(f"{x['year']}-{slam_dates[x['slam']]}"), axis=1)
matches['surface'] = matches['slam'].map(surface_map)

# Attach ATP/WTA Tour flag based on match_id (Starts with 1 = ATP, else WTA)
matches['tour'] = np.where(matches['match_id'].str.split('-').str[-1].astype(str).str.startswith('1'), 'ATP', 'WTA')

# Merge DOBs and calculate age (Fallback to 25 if missing)
matches = matches.merge(players[['full_name', 'dob']], left_on='player1', right_on='full_name', how='left').rename(columns={'dob': 'p1_dob'})
matches = matches.merge(players[['full_name', 'dob']], left_on='player2', right_on='full_name', how='left').rename(columns={'dob': 'p2_dob'})

matches['p1_age'] = np.floor((matches['tourney_date'] - matches['p1_dob']).dt.days / 365.25).fillna(25).astype(int)
matches['p2_age'] = np.floor((matches['tourney_date'] - matches['p2_dob']).dt.days / 365.25).fillna(25).astype(int)

# --- 4. AGGREGATE POINT STATS & FLAVOR STATS ---
print("Aggregating point-by-point stats...")
points['PointServer'] = pd.to_numeric(points['PointServer'], errors='coerce')
points['PointWinner'] = pd.to_numeric(points['PointWinner'], errors='coerce')

# Base Probabilities Setup
points['p1_serve_won'] = np.where((points['PointServer']==1) & (points['PointWinner']==1), 1, 0)
points['p1_serve_total'] = np.where(points['PointServer']==1, 1, 0)
points['p1_ret_won'] = np.where((points['PointServer']==2) & (points['PointWinner']==1), 1, 0)
points['p1_ret_total'] = np.where(points['PointServer']==2, 1, 0)

points['p2_serve_won'] = np.where((points['PointServer']==2) & (points['PointWinner']==2), 1, 0)
points['p2_serve_total'] = np.where(points['PointServer']==2, 1, 0)
points['p2_ret_won'] = np.where((points['PointServer']==1) & (points['PointWinner']==2), 1, 0)
points['p2_ret_total'] = np.where(points['PointServer']==1, 1, 0)

# Flavor Stats Setup (Force numeric)
flavor_cols = ['P1Ace', 'P2Ace', 'P1DoubleFault', 'P2DoubleFault', 'P1Winner', 'P2Winner', 
               'P1UnfErr', 'P2UnfErr', 'P1BreakPoint', 'P2BreakPoint', 'P1BreakPointWon', 'P2BreakPointWon']
for col in flavor_cols:
    points[col] = pd.to_numeric(points[col], errors='coerce').fillna(0)

# Group by match_id
stats = points.groupby('match_id').agg({
    'p1_serve_won': 'sum', 'p1_serve_total': 'sum', 'p1_ret_won': 'sum', 'p1_ret_total': 'sum',
    'p2_serve_won': 'sum', 'p2_serve_total': 'sum', 'p2_ret_won': 'sum', 'p2_ret_total': 'sum',
    **{c: 'sum' for c in flavor_cols}
}).reset_index()

# Calculate final match-level p_serve and p_return to avoid division by zero
stats['p1_p_serve'] = np.where(stats['p1_serve_total'] > 0, stats['p1_serve_won'] / stats['p1_serve_total'], 0)
stats['p1_p_return'] = np.where(stats['p1_ret_total'] > 0, stats['p1_ret_won'] / stats['p1_ret_total'], 0)
stats['p2_p_serve'] = np.where(stats['p2_serve_total'] > 0, stats['p2_serve_won'] / stats['p2_serve_total'], 0)
stats['p2_p_return'] = np.where(stats['p2_ret_total'] > 0, stats['p2_ret_won'] / stats['p2_ret_total'], 0)

# --- 5. MERGE EVERYTHING ---
final_df = matches.merge(stats, on='match_id', how='inner')

# --- 6. BUILD THE JSON BRAIN ---
print("Constructing the JSON Brain...")
database = {}

def update_player_stats(name, age, tour, surface, p_serve, p_return, aces, dfs, winners, errors, bp_won, bp_total):
    name = str(name).strip().lower()
    if pd.isna(name) or name == 'nan': return
    age = str(int(age))
    surface = str(surface).strip()

    if name not in database:
        database[name] = {"tour": tour, "ages": {}}
    if age not in database[name]["ages"]:
        database[name]["ages"][age] = {}
    if surface not in database[name]["ages"][age]:
        database[name]["ages"][age][surface] = {
            "matches": 0, "p_serve_total": 0, "p_return_total": 0,
            "aces": 0, "dfs": 0, "winners": 0, "errors": 0, "bp_won": 0, "bp_total": 0
        }

    s = database[name]["ages"][age][surface]
    s["matches"] += 1
    s["p_serve_total"] += p_serve
    s["p_return_total"] += p_return
    s["aces"] += aces
    s["dfs"] += dfs
    s["winners"] += winners
    s["errors"] += errors
    s["bp_won"] += bp_won
    s["bp_total"] += bp_total

# Populate the dictionary
for _, row in final_df.iterrows():
    tour = row.get('tour', 'ATP')
    surface = row.get('surface', 'Hard')
    
    # Process Player 1
    update_player_stats(
        row.get('player1'), row.get('p1_age'), tour, surface,
        row.get('p1_p_serve', 0), row.get('p1_p_return', 0),
        row.get('P1Ace', 0), row.get('P1DoubleFault', 0),
        row.get('P1Winner', 0), row.get('P1UnfErr', 0),
        row.get('P1BreakPointWon', 0), row.get('P1BreakPoint', 0)
    )
    
    # Process Player 2
    update_player_stats(
        row.get('player2'), row.get('p2_age'), tour, surface,
        row.get('p2_p_serve', 0), row.get('p2_p_return', 0),
        row.get('P2Ace', 0), row.get('P2DoubleFault', 0),
        row.get('P2Winner', 0), row.get('P2UnfErr', 0),
        row.get('P2BreakPointWon', 0), row.get('P2BreakPoint', 0)
    )

# Calculate final averages and format beautifully
final_database = {}
for player in sorted(database.keys()):
    data = database[player]
    final_database[player] = {"tour": data["tour"], "ages": {}}
    
    for age in sorted(data["ages"].keys(), key=lambda x: int(x) if x.isdigit() else 999):
        final_database[player]["ages"][age] = {}
        for surface, s in data["ages"][age].items():
            m = s["matches"]
            if m == 0: continue
            bp_conversion = (s["bp_won"] / s["bp_total"] * 100) if s["bp_total"] > 0 else 0
            
            final_database[player]["ages"][age][surface] = {
                "p_serve": round(s["p_serve_total"] / m, 4),
                "p_return": round(s["p_return_total"] / m, 4),
                "matches": m,
                "avg_aces": round(s["aces"] / m, 1),
                "avg_dfs": round(s["dfs"] / m, 1),
                "avg_winners": round(s["winners"] / m, 1),
                "avg_errors": round(s["errors"] / m, 1),
                "bp_conversion_pct": round(bp_conversion, 1)
            }

print("Saving player_profiles_master.json...")
with open("player_profiles_master.json", "w") as f:
    json.dump(final_database, f, indent=4)

print("Pipeline Complete! File saved successfully.")