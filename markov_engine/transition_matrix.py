def calculate_game_win_probability(p: float) -> float:
    # State representation: (server_points, receiver_points)
    # p is the probability that the server wins a point.
    
    # Initialize the probability of being in state (0, 0) as 1.0
    current_states = {(0, 0): 1.0}
    
    server_win_prob = 0.0
    
    # A single game maxes out at 6 points before someone wins or Deuce is reached.
    for _ in range(6):
        next_states = {}
        for (s, r), prob in current_states.items():
            
            # If server wins the point
            if s == 3 and r < 3:
                # Server wins the game (Hold)
                server_win_prob += prob * p
            elif s == 2 and r == 3:
                # Reaches Deuce (3, 3)
                next_states[(3, 3)] = next_states.get((3, 3), 0.0) + prob * p
            elif s < 3:
                # Normal point progression
                next_states[(s + 1, r)] = next_states.get((s + 1, r), 0.0) + prob * p
                
            # If receiver wins the point
            if r == 3 and s < 3:
                # Receiver wins the game (Break)
                pass 
            elif s == 3 and r == 2:
                # Reaches Deuce (3, 3)
                next_states[(3, 3)] = next_states.get((3, 3), 0.0) + prob * (1.0 - p)
            elif r < 3:
                # Normal point progression
                next_states[(s, r + 1)] = next_states.get((s, r + 1), 0.0) + prob * (1.0 - p)
                
        current_states = next_states
        
    # By this point, the only non-absorbing state left is Deuce (3, 3)
    deuce_prob = current_states.get((3, 3), 0.0)
    
    # Math Shortcut formula for Deuce resolving immediately
    # Math shortcut given: p^2 / (p^2 + (1-p)^2)
    p_deuce_win = (p**2) / (p**2 + (1.0 - p)**2)
    
    total_win_prob = server_win_prob + (deuce_prob * p_deuce_win)
    return total_win_prob

if __name__ == "__main__":
    p_val = 0.60
    prob = calculate_game_win_probability(p_val)
    percentage = prob * 100
    print(f"Game-win probability: {percentage:.2f}%")
    
    # Automated test inside the script
    assert abs(percentage - 73.57) < 0.01, f"Expected ~73.57%, got {percentage:.2f}%"
    print("Test passed successfully.")