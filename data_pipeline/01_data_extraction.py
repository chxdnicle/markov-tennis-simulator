import pandas as pd
import os

print("Starting Data Ingestion and Extraction Pipeline...\n")

# --- 1. PIPELINE SETTINGS ---
# Set these to the relative folder paths in your GitHub repo
match_folder_path = "Grandslam_data"
points_folder_path = "points_data" 
# (Note: You can change these paths if you put all raw CSVs in a single 'data' folder)

start_year = 2011
end_year = 2024
years = range(start_year, end_year + 1)
slams = ['ausopen', 'frenchopen', 'wimbledon', 'usopen']

# --- 2. MATCH DATA EXTRACTION ---
print("="*50)
print("PHASE 1: HARVESTING MATCH METADATA")
print("="*50)

# The exact columns needed from the messy match CSVs
match_columns_to_keep = ['match_id', 'year', 'slam', 'match_num', 'player1', 'player2']

match_df_list = []
total_match_rows = 0
match_files_processed = 0

for year in years:
    for slam in slams:
        filepath = os.path.join(match_folder_path, f"{year}-{slam}-matches.csv")

        if os.path.exists(filepath):
            try:
                # Read the CSV
                df = pd.read_csv(filepath)
                
                # Check rows and filter to exact columns
                current_rows = len(df)
                df = df[match_columns_to_keep].copy()
                
                # Add to tracking
                match_df_list.append(df)
                total_match_rows += current_rows
                match_files_processed += 1
                
                print(f"Match data extracted: {year} {slam} ({current_rows} rows)")

            except Exception as e:
                print(f"Error reading {filepath}: {e}")

# Unify the match data
if match_df_list:
    master_match_df = pd.concat(match_df_list, ignore_index=True)
    match_output_path = "master_match_data.csv"
    master_match_df.to_csv(match_output_path, index=False)
    print(f"\nSUCCESS: Unified {match_files_processed} match files into '{match_output_path}'")
    print(f"Total Master Match Rows: {total_match_rows}\n")
else:
    print("\nWARNING: No match files found. Check your folder paths.")


# --- 3. POINT DATA EXTRACTION ---
print("="*50)
print("PHASE 2: HARVESTING STRICT-SCHEMA POINT DATA")
print("="*50)

# The exact 34 columns required for the simulator engine
point_target_columns = [
    'match_id', 'ElapsedTime', 'SetNo', 'P1GamesWon', 'P2GamesWon', 'SetWinner',
    'GameNo', 'GameWinner', 'PointNumber', 'PointWinner', 'PointServer',
    'Speed_KMH', 'Rally', 'P1Score', 'P2Score', 'P1Momentum', 'P2Momentum',
    'P1PointsWon', 'P2PointsWon', 'P1Ace', 'P2Ace', 'P1Winner', 'P2Winner',
    'P1DoubleFault', 'P2DoubleFault', 'P1UnfErr', 'P2UnfErr', 'P1NetPoint',
    'P2NetPoint', 'P1NetPointWon', 'P2NetPointWon', 'P1BreakPoint',
    'P2BreakPoint', 'P1BreakPointWon', 'P2BreakPointWon'
]

point_df_list = []
total_points_processed = 0
point_files_processed = 0

for year in years:
    for slam in slams:
        # Handle historical tournament cancellations / missing data logic
        if year == 2020 and slam == 'wimbledon': 
            continue
        if year >= 2022 and slam in ['ausopen', 'frenchopen']: 
            continue

        filename = f"{year}-{slam}-points.csv"
        file_path = os.path.join(points_folder_path, filename)

        if os.path.exists(file_path):
            try:
                # Load the raw file safely (low_memory=False prevents mixed-type crashes)
                df_temp = pd.read_csv(file_path, low_memory=False)

                # THE SCHEMA FIX: Force the dataframe to exactly match the 34 target columns.
                # Fills missing columns with NaN, drops extra unused columns.
                df_clean = df_temp.reindex(columns=point_target_columns)

                point_df_list.append(df_clean)
                total_points_processed += len(df_clean)
                point_files_processed += 1

                print(f"Point data extracted: {filename} ({len(df_clean)} rows)")

            except Exception as e:
                print(f"Error processing {filename}: {e}")

# Unify the point data
if point_df_list:
    print("\nExecuting final merge of all point data (This may take a moment)...")
    final_point_master_df = pd.concat(point_df_list, ignore_index=True)
    
    point_output_path = "master_point_data.csv"
    final_point_master_df.to_csv(point_output_path, index=False)
    
    print("\n" + "="*50)
    print("PIPELINE COMPLETE: ALL DATA EXTRACTED AND UNIFIED")
    print("="*50)
    print(f"Total Point Files Processed: {point_files_processed}")
    print(f"Total Master Point Rows: {len(final_point_master_df):,}")
    print(f"Total Master Columns Enforced: {len(final_point_master_df.columns)}")
    print(f"Saved to: '{point_output_path}'")
    print("="*50)
else:
    print("\nWARNING: No point files found. Check your folder paths.")