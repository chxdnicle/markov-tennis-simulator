# 🎾 Markov Tennis Simulator

**[🌍 Click Here to View the Live Simulator Website](https://chxdnicle.github.io/grandslamsimulator)**

A custom probability engine built on **1.9 million historical data points** to predict ATP/WTA Grand Slam matchups. 

Instead of relying on arbitrary player rankings or static win percentages, this engine translates historical point-by-point telemetry into a **Markov Chain state machine**. It bypasses subjective opinions by simulating the exact rules of tennis point-by-point, running **10,000 Monte Carlo simulations** per matchup to output a definitive, mathematically sound win probability.

---

### 💻 Technologies
* **Python** (Core Logic)
* **Pandas & NumPy** (Data Extraction & Feature Engineering)
* **Probability & Statistics** (Markov Chains, Monte Carlo Methods)
* **JSON** (NoSQL Data Structuring)
* **Git & GitHub** (Version Control)

---

### ✨ Features
* **Point-by-Point Simulation:** Simulates every single point, game, and set of a Best-of-5 match using true historical serve/return probabilities.
* **Surface-Specific Physics:** Adjusts predictions based on court surface (Hard, Clay, Grass), knowing that a player's `p_serve` on Grass is vastly different than on Clay.
* **Predictive Scorelines:** Outputs not just the winner, but the exact probabilistic odds of a 3-0, 3-1, or 3-2 victory.
* **Deep Stat Tracking:** Uses a pre-computed JSON "Brain" containing granular data like Ace averages, Double Faults, Unforced Errors, and Break Point conversion rates.

---

### ⚙️ The Process
This project was broken down into a strict two-part architecture:
1. **The Data Pipeline:** I ingested 49 separate CSV files containing over 1.9 million points from Grand Slams (2011–2024). I wrote scripts to handle missing data (`NaN` imputation), standardizing messy player names (building a custom mapping dictionary), and calculating player ages on the exact day of the tournament.
2. **The Execution Engine:** I aggregated the millions of rows into two master metrics: `p_serve` and `p_return`. I then built a mathematical transition matrix to handle complex tennis rules (like a custom formula to mathematically resolve infinite Deuce loops) and wrapped it in a 10,000-loop execution script.

---

### 🧠 What I Learned
* **The "Rearview Mirror" Flaw:** I learned a massive lesson in predictive data science. Historical models lag behind real-time human breakouts. The engine struggled to predict a 20-year-old Ben Shelton's explosive 2023 US Open run because it judged him on his limited past, not his current momentum. 
* **Handling Massive Data:** I learned how to efficiently group and aggregate millions of rows without crashing my machine, and why separating raw data from the execution engine is vital for performance.
* **Domain Knowledge is Key:** You can't just write math; you have to understand the sport. Building the Deuce and Advantage logic required combining coding skills with real-world tennis rules.

---

### 📈 Overall Growth
This project marked a massive shift in my mindset. I transitioned from just *analyzing* past data (creating charts and dashboards) to actually building a **predictive engine**. It improved my architectural thinking, forcing me to design a clean data pipeline that feeds into a lightweight, executable backend. 

---

### 🚀 How It Can Be Improved
* **Recent Form / Elo Weighting:** To fix the "Rearview Mirror" flaw, the next iteration will weigh matches from the last 3 months much heavier than matches from 3 years ago, allowing the engine to detect "momentum."
* **Live API Integration:** Swapping out static CSV historical data for a live API feed to update player stats instantly after every real-world tournament.

---

### 🖥️ Running the Project

**Note on Data Limits:** The raw 1.9M row dataset exceeds GitHub's limits and is not included. You cannot run the data extraction scripts locally. However, you **can** run the execution engine using the provided JSON brain!

1. Clone this repository.
2. Navigate to the project folder in your terminal.
3. Run the interactive CLI:
   ```bash
   python monte_carlo_simulator.py
4. Enter Player 1, Player 2, and the Surface when prompted to see the engine run 10,000 simulations in real-time.

---

### 🎥 Video Demo
Watch exactly how the Markov engine works

https://github.com/user-attachments/assets/0378aafb-4787-46e5-837b-0fbad8afc1ac

In the demo above, you can see the engine in action. To run a matchup, first select the Tour (ATP/WTA), then choose Player 1 and Player 2, and lock in the Court Surface and Age for each. Once you click Start Simulations, the engine crunches 10,000 Monte Carlo runs in the background. The results instantly populate below: the Prediction Box reveals the ultimate probabilistic winner, while the Set Score Probability breaks down the exact score-line odds. Finally, you can interact with the Player Stats card on the left—just flip it back and forth to compare the underlying historical metrics driving the simulation for both players!




