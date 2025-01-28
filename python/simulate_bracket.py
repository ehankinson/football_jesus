from stats import Stats
from simulate import Simulate
from playoff_bracket import generate_playoff_bracket, print_bracket, get_round_matchups, update_bracket

# YEAR = 2023
conferences = {
    "AFC": [
        ("KAN", 1, 2007),  
        ("BUF", 2, 2021),  
        ("BAL", 3, 2023),  
        ("HOU", 4, 2024),  
        ("LAC", 5, 2023),
        ("KAN", 6, 2022),
        ("BUF", 7, 2022),
        ("MIA", 8, 2023),
        ("DEN", 9, 2024),
        ("KAN", 10, 2021),
        ("NWE", 11, 2021),
        ("IND", 12, 2021),
        ("CIN", 13, 2022),
        ("LAC", 14, 2024),
        ("KAN", 15, 2023),
        ("BAL", 16, 2022)
    ],
    "NFC": [
        ("DET", 1, 2024),  
        ("SFO", 2, 1989),  
        ("SFO", 3, 2023),  
        ("PHI", 4, 2024),  
        ("TAM", 5, 2021),
        ("SFO", 6, 2022),
        ("GNB", 7, 2024),
        ("DAL", 8, 2021),
        ("DAL", 9, 2022),
        ("DAL", 10, 2023),
        ("TAM", 11, 2024),
        ("DET", 12, 2023),
        ("LAR", 13, 2021),
        ("GNB", 14, 2021),
        ("MIN", 15, 2024),
        ("WAS", 16, 2024),
    ]
}

byes_per_conf = {
    "AFC": 0,
    "NFC": 0
}

stats = {}
simulate = Simulate()

# Generate bracket
bracket = generate_playoff_bracket(conferences, byes_per_conf)
print_bracket(bracket)

for rnd in range(1, 6):
    matchups = get_round_matchups(bracket, rnd)
    
    for idx, game in enumerate(matchups):
        home_team = game['team1'][:3]
        home_year = game['team1_year']
        away_team = game['team2'][:3]
        away_year = game['team2_year']

        if home_year == away_year:
            if home_year not in stats:
                stats[home_year] = Stats(home_year)
        else:
            if home_year not in stats:
                stats[home_year] = Stats(home_year)
            
            if away_year not in stats:
                stats[away_year] = Stats(away_year)
        

        winner = simulate.simulate_games(home_team, stats[home_year], away_team, stats[away_year], 10_000)
        winner_year = home_year if winner == home_team else away_year
        update_bracket(bracket, rnd, idx, f"{winner}-{winner_year}")
    
print_bracket(bracket)
