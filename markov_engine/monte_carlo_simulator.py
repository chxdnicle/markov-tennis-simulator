import random
import json
import os

# Import the math rules from your other file
# Make sure your transition matrix file is named transition_matrix.py!
from transition_matrix import calculate_game_win_probability

def simulate_set(p1_game_prob, p2_game_prob):
    """Simulates a single set. Returns 1 if Player 1 wins, 2 if Player 2 wins."""
    p1_games = 0
    p2_games = 0
    
    while True:
        # Player 1 serves
        if random.random() < p1_game_prob:
            p1_games += 1
        else:
            p2_games += 1
            
        if (p1_games >= 6 and p1_games - p2_games >= 2) or p1_games == 7:
            return 1
        if (p2_games >= 6 and p2_games - p1_games >= 2) or p2_games == 7:
            return 2
            
        # Player 2 serves
        if random.random() < p2_game_prob:
            p2_games += 1
        else:
            p1_games += 1
            
        if (p1_games >= 6 and p1_games - p2_games >= 2) or p1_games == 7:
            return 1
        if (p2_games >= 6 and p2_games - p1_games >= 2) or p2_games == 7:
            return 2

def run_simulation(p1_name, p2_name, surface, num_simulations=10000):
    # Load the Database
    script_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(script_dir, 'player_profiles_master.json')
    
    if not os.path.exists(json_path):
        print(f"Error: Could not find {json_path}")
        return

    with open(json_path, 'r') as file:
        database = json.load(file)

    p1_name = p1_name.lower()
    p2_name = p2_name.lower()

    if p1_name not in database:
        print(f"Error: Player '{p1_name}' not found in database.")
        return
    if p2_name not in database:
        print(f"Error: Player '{p2_name}' not found in database.")
        return

    # For simplicity in this terminal script, we just grab their overall average across all ages
    # (Since we removed the FastAPI age-selector logic)
    def get_avg_stats(player_data, target_surface):
        total_p_serve = 0
        total_p_return = 0
        count = 0
        for age, surfaces in player_data['ages'].items():
            if target_surface in surfaces:
                total_p_serve += surfaces[target_surface]['p_serve']
                total_p_return += surfaces[target_surface]['p_return']
                count += 1
        if count == 0:
            return None
        return (total_p_serve / count, total_p_return / count)

    p1_stats = get_avg_stats(database[p1_name], surface)
    p2_stats = get_avg_stats(database[p2_name], surface)

    if not p1_stats or not p2_stats:
        print(f"Error: Not enough data for these players on {surface}.")
        return

    p1_p_serve, p1_p_return = p1_stats
    p2_p_serve, p2_p_return = p2_stats

    # Calculate the exact game win probabilities using your transition matrix
    p1_hold_prob = calculate_game_win_probability(p1_p_serve)
    p2_hold_prob = calculate_game_win_probability(p2_p_serve)

    print(f"\n[ENGINE WARMUP] {p1_name.title()} Hold %: {p1_hold_prob*100:.1f}%")
    print(f"[ENGINE WARMUP] {p2_name.title()} Hold %: {p2_hold_prob*100:.1f}%\n")
    print(f"Running {num_simulations:,} Grand Slam Best-of-5 Simulations...")

    # The Execution Loop
    p1_match_wins = 0
    p2_match_wins = 0
    
    # Track Set Scores
    sets_3_0 = 0
    sets_3_1 = 0
    sets_3_2 = 0

    for _ in range(num_simulations):
        p1_sets = 0
        p2_sets = 0
        
        while p1_sets < 3 and p2_sets < 3:
            winner = simulate_set(p1_hold_prob, p2_hold_prob)
            if winner == 1:
                p1_sets += 1
            else:
                p2_sets += 1
                
        if p1_sets == 3:
            p1_match_wins += 1
            if p2_sets == 0: sets_3_0 += 1
            elif p2_sets == 1: sets_3_1 += 1
            elif p2_sets == 2: sets_3_2 += 1
        else:
            p2_match_wins += 1

    # Output the Final Report
    p1_win_pct = (p1_match_wins / num_simulations) * 100
    p2_win_pct = (p2_match_wins / num_simulations) * 100
    
    odds_3_0 = (sets_3_0 / p1_match_wins * 100) if p1_match_wins > 0 else 0
    odds_3_1 = (sets_3_1 / p1_match_wins * 100) if p1_match_wins > 0 else 0
    odds_3_2 = (sets_3_2 / p1_match_wins * 100) if p1_match_wins > 0 else 0

    overall_winner = p1_name.title() if p1_match_wins > p2_match_wins else p2_name.title()
    winner_prob = max(p1_win_pct, p2_win_pct)

    print("="*50)
    print("🎾 SIMULATION REPORT 🎾")
    print("="*50)
    print(f"Matchup: {p1_name.title()} vs {p2_name.title()}")
    print(f"Surface: {surface}")
    print("-" * 50)
    print(f"🏆 PREDICTED WINNER: {overall_winner}")
    print(f"WIN PROBABILITY:    {winner_prob:.1f}%")
    if overall_winner == p1_name.title():
        print(f"\nMost Likely Scorelines for {p1_name.title()}:")
        print(f"  3-0 Win: {odds_3_0:.1f}%")
        print(f"  3-1 Win: {odds_3_1:.1f}%")
        print(f"  3-2 Win: {odds_3_2:.1f}%")
    print("="*50 + "\n")

# --- INTERACTIVE TERMINAL LOOP ---
if __name__ == "__main__":
    print("\n" + "="*50)
    print("INITIALIZING V8 MARKOV ENGINE...")
    print("="*50)
    
    while True:
        p1 = input("\nEnter Player 1 Name (or 'quit' to exit): ").strip()
        if p1.lower() == 'quit':
            break
            
        p2 = input("Enter Player 2 Name: ").strip()
        surface = input("Enter Surface (Hard, Clay, Grass): ").strip().capitalize()
        
        if surface not in ['Hard', 'Clay', 'Grass']:
            print("Invalid surface. Defaulting to Hard.")
            surface = 'Hard'
            
        try:
            run_simulation(p1, p2, surface)
        except Exception as e:
            print(f"Simulation failed: {e}")