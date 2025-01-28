import json
import random
from tqdm import tqdm
from stats import Stats
from simulate import Simulate



def calculate_new_ratings(player1_rating, player2_rating, result, k=45):
    # Expected scores for both players
    expected1 = 1 / (1 + 10 ** ((player2_rating - player1_rating) / 400))
    expected2 = 1 - expected1

    # Update ratings based on result
    new_rating1 = player1_rating + k * (result - expected1)
    new_rating2 = player2_rating + k * ((1 - result) - expected2)

    return round(new_rating1), round(new_rating2)



def create_sch(teams: dict, opponent_amount: int):
    schedule = []
    teams_list = [(team[:3], int(team[4:])) for team in teams.keys()]

    for i in range(len(teams_list)):
        home_name, home_year = teams_list[i]
        for j in range(i + 1, len(teams_list)):
            away_name, away_year = teams_list[j]
            # Generate all matches at once for the given opponent_amount
            schedule.extend([[home_name, home_year, "vs", away_name, away_year]] * opponent_amount)
    
    random.shuffle(schedule)
    return schedule


if __name__ == '__main__':
    year = 2021
    with open(f"json/ratings_{year}.json", "r") as j:
        teams = json.load(j)
    
    simulate = Simulate()
    stats = {}

    schedule = create_sch(teams, 10000)

    for game in tqdm(schedule):
        home_team = game[0]
        home_year = game[1]
        away_team = game[3]
        away_year = game[4]

        home_key = f"{home_team}-{home_year}"
        away_key = f"{away_team}-{away_year}"

        if home_year == away_year:
            if home_year not in stats:
                stats[home_year] = Stats(home_year)
        else:
            if home_year not in stats:
                stats[home_year] = Stats(home_year)
            if away_year not in stats:
                stats[away_year] = Stats(away_year)

        result = simulate.simulate_game(home_team, stats[home_year], away_team, stats[away_year])

        if result == 1:
            result = 1
            teams[home_key]['wins'] += 1
            teams[away_key]['losses'] += 1
        elif result == -1:
            result = 0
            teams[away_key]['wins'] += 1
            teams[home_key]['losses'] += 1
        else:
            result = 0.5
            teams[away_key]['ties'] += 1
            teams[home_key]['ties'] += 1

        teams[home_key]["rating"], teams[away_key]["rating"] = calculate_new_ratings(teams[home_key]["rating"], teams[away_key]["rating"], result)

    sorted_teams = sorted(teams.items(), key=lambda x: x[1]['rating'], reverse=True)

    # Print sorted rankings
    print("\nTeam Rankings:")
    for rank, (team, data) in enumerate(sorted_teams, start=1):
        print(f"{rank}. {team} (Rating: {data['rating']}), wins: {teams[team]['wins']}, losses: {teams[team]['losses']}, ties: {teams[team]['ties']}")


    with open(f"json/ratings_{year}.json", "w") as j:
        json.dump(teams, j, indent=2)

    with open(f"json/ratings_{year}.json", "r") as j:
        teams = json.load(j)
    
    new_teams = []
    for team in teams:
        add = [team, teams[team]['wins'] / (teams[team]['wins'] + teams[team]['losses'])]
        new_teams.append(add)
    
    sorted_teams = sorted(new_teams, key=lambda x: x[1], reverse=True)

    for i, team in enumerate(sorted_teams):
        print(f"{i}, {team}")

