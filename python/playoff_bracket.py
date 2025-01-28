from typing import List, Dict, Optional
import math



def generate_playoff_bracket(conferences: Dict[str, List[tuple[str, int, int]]], byes_per_conf: Dict[str, int], reseed: bool = True) -> Dict:
    """
    Generate a playoff bracket with conferences and seeding.
    
    Args:
        conferences: Dictionary with conference names as keys and list of (team, seed, year) tuples as values
        byes_per_conf: Dictionary with conference names as keys and number of byes as values
        reseed: Whether to reseed teams after each round (default: True)
        
    Returns:
        Dictionary containing the bracket structure with rounds and matchups
    """
    # Store original seeds and years for reseeding
    team_info = {}
    for conf, teams in conferences.items():
        for team, seed, year in teams:
            if not isinstance(year, int) or year < 1920:
                raise ValueError(f"Invalid year for team {team}: {year}. Year must be an integer >= 1920")
            team_id = f"{team}-{year}"  # Create unique team identifier
            team_info[team_id] = (seed, conf, year)
    
    bracket = {
        "num_rounds": math.ceil(math.log2(sum(len(teams) for teams in conferences.values()))),
        "rounds": {},
        "conferences": list(conferences.keys()),
        "team_info": team_info,
        "reseed": reseed
    }
    
    # Validate inputs
    for conf, teams in conferences.items():
        if conf not in byes_per_conf:
            raise ValueError(f"Conference {conf} not found in byes_per_conf")
            
        num_byes = byes_per_conf[conf]
        if num_byes >= len(teams):
            raise ValueError(f"Number of byes ({num_byes}) cannot be greater than or equal to number of teams in conference {conf} ({len(teams)})")
        
        # Sort teams by seed
        teams.sort(key=lambda x: x[1])
    
    # Calculate total teams and rounds
    total_teams = sum(len(teams) for teams in conferences.values())
    num_rounds = math.ceil(math.log2(total_teams))
    perfect_bracket_size = 2 ** num_rounds
    
    # Set up first round for each conference
    first_round = []
    teams_with_byes = []
    
    for conf, teams in conferences.items():
        # Get bye teams (top seeds)
        num_byes = byes_per_conf[conf]
        conf_byes = teams[:num_byes]
        teams_with_byes.extend((f"{team[0]}-{team[2]}", conf) for team in conf_byes)  # Include year in team ID
        
        # Get remaining teams for first round and sort by seed
        remaining_teams = teams[num_byes:]
        num_remaining = len(remaining_teams)
        
        # Create matchups based on seeding (highest vs lowest)
        for i in range(num_remaining // 2):
            high_seed = remaining_teams[i]
            low_seed = remaining_teams[-(i + 1)]
            matchup = {
                "team1": f"{high_seed[0]}-{high_seed[2]}",  # Include year in team ID
                "team2": f"{low_seed[0]}-{low_seed[2]}",    # Include year in team ID
                "conference": conf,
                "winner": None
            }
            first_round.append(matchup)
        
        # Handle odd number of teams if necessary
        if num_remaining % 2 == 1:
            middle_team = remaining_teams[num_remaining // 2]
            team_id = f"{middle_team[0]}-{middle_team[2]}"  # Include year in team ID
            matchup = {
                "team1": team_id,
                "team2": None,
                "conference": conf,
                "winner": team_id  # Automatic win if no opponent
            }
            first_round.append(matchup)
    
    bracket["rounds"][1] = {
        "matchups": first_round,
        "teams_with_byes": teams_with_byes
    }
    
    # Set up subsequent rounds
    for round_num in range(2, num_rounds + 1):
        prev_round_matchups = len(bracket["rounds"][round_num - 1]["matchups"])
        prev_round_byes = len(bracket["rounds"][round_num - 1]["teams_with_byes"])
        total_teams_next = prev_round_matchups + prev_round_byes
        
        matchups = []
        for _ in range(total_teams_next // 2):
            matchups.append({
                "team1": None,
                "team2": None,
                "conference": None,  # Conference may mix in later rounds
                "winner": None
            })
        
        bracket["rounds"][round_num] = {
            "matchups": matchups,
            "teams_with_byes": []
        }
    
    return bracket



def reseed_round(bracket: Dict, round_num: int) -> Dict:
    """
    Reseed the matchups in a round based on team seeds.
    Teams from the same conference play each other until the final round.
    Highest seeds play lowest remaining seeds.
    
    Args:
        bracket: The current bracket structure
        round_num: The round number to reseed
    """
    if not bracket["reseed"] or round_num <= 1:
        return bracket
    
    # Get all teams that will play in this round, separated by conference
    teams_by_conf = {conf: [] for conf in bracket["conferences"]}
    
    # Add teams with byes from previous round
    prev_round = round_num - 1
    if prev_round in bracket["rounds"]:
        bye_teams = bracket["rounds"][prev_round]["teams_with_byes"]
        for team, conf in bye_teams:
            seed, conf, _ = bracket["team_info"][team]  # Unpack all three values
            teams_by_conf[conf].append((team, seed))
    
    # Add winners from previous round
    if prev_round in bracket["rounds"]:
        for matchup in bracket["rounds"][prev_round]["matchups"]:
            if matchup["winner"]:
                team = matchup["winner"]
                seed, conf, _ = bracket["team_info"][team]  # Unpack all three values
                teams_by_conf[conf].append((team, seed))
    
    # Sort teams by seed within each conference
    for conf in teams_by_conf:
        teams_by_conf[conf].sort(key=lambda x: x[1])  # Sort by seed (1 is highest)
    
    # Create matchups based on seeding, keeping conferences separate until final round
    matchups = []
    if round_num == bracket["num_rounds"]:  # Final round
        # Combine all teams and sort by seed
        all_teams = []
        for conf_teams in teams_by_conf.values():
            all_teams.extend(conf_teams)
        all_teams.sort(key=lambda x: x[1])
        
        # Create final matchup
        if len(all_teams) >= 2:
            matchups.append({
                "team1": all_teams[0][0],
                "team2": all_teams[1][0],
                "conference": None,
                "winner": None
            })
    else:  # Earlier rounds - keep conferences separate
        for conf, teams in teams_by_conf.items():
            num_teams = len(teams)
            # Match highest seeds with lowest seeds
            for i in range(num_teams // 2):
                high_seed = teams[i]  # Get highest seed
                low_seed = teams[-(i + 1)]  # Get corresponding lowest seed
                matchup = {
                    "team1": high_seed[0],
                    "team2": low_seed[0],
                    "conference": conf,
                    "winner": None
                }
                matchups.append(matchup)
            
            if num_teams % 2 == 1:
                # Handle odd number of teams
                middle_team = teams[num_teams // 2]
                matchup = {
                    "team1": middle_team[0],
                    "team2": None,
                    "conference": conf,
                    "winner": middle_team[0]
                }
                matchups.append(matchup)
    
    bracket["rounds"][round_num]["matchups"] = matchups
    return bracket



def update_bracket(bracket: Dict, round_num: int, matchup_index: int, winner: str) -> Dict:
    """
    Update a bracket with the winner of a matchup.
    
    Args:
        bracket: The current bracket structure
        round_num: The round number of the matchup
        matchup_index: The index of the matchup in the round
        winner: The winning team
        
    Returns:
        Updated bracket structure
    """
    if round_num not in bracket["rounds"]:
        raise ValueError(f"Invalid round number: {round_num}")
    
    if matchup_index >= len(bracket["rounds"][round_num]["matchups"]):
        raise ValueError(f"Invalid matchup index for round {round_num}")
    
    # Update the winner
    bracket["rounds"][round_num]["matchups"][matchup_index]["winner"] = winner
    
    # Check if all matchups in current round have winners
    current_round = bracket["rounds"][round_num]
    all_matchups_complete = all(matchup["winner"] is not None for matchup in current_round["matchups"])
    
    if all_matchups_complete and round_num < bracket["num_rounds"]:
        # Reseed next round if enabled
        if bracket["reseed"]:
            bracket = reseed_round(bracket, round_num + 1)
    
    return bracket



def print_bracket(bracket: Dict) -> None:
    """
    Print a human-readable version of the bracket with conferences and years.
    """
    for round_num in range(1, bracket["num_rounds"] + 1):
        print(f"\nRound {round_num}:")
        
        # For Round 2, pre-fill the matchups with bye teams
        if round_num == 2:
            bye_teams = bracket['rounds'][1]['teams_with_byes']
            matchups = bracket['rounds'][round_num]['matchups']
            teams_by_conf = {conf: [] for conf in bracket["conferences"]}
            
            # Group bye teams by conference
            for team, conf in bye_teams:
                teams_by_conf[conf].append(team)
            
            # Place bye teams in their conference's matchups
            conf_matchup_index = {conf: 0 for conf in bracket["conferences"]}
            for i, matchup in enumerate(matchups):
                conf = matchup['conference']
                if conf and teams_by_conf[conf] and not matchup['team1']:
                    matchup['team1'] = teams_by_conf[conf].pop(0)
        
        for i, matchup in enumerate(bracket['rounds'][round_num]['matchups'], 1):
            team1 = matchup['team1'] or "TBD"
            team2 = matchup['team2'] or "TBD"
            
            # Format team names with years
            if team1 != "TBD":
                team_name = team1.split('-')[0]  # Extract team name from ID
                year = bracket["team_info"][team1][2]
                team1 = f"{team_name} ({year})"
            if team2 != "TBD":
                team_name = team2.split('-')[0]  # Extract team name from ID
                year = bracket["team_info"][team2][2]
                team2 = f"{team_name} ({year})"
            
            conf = f" ({matchup['conference']})" if matchup['conference'] else ""
            winner = ""
            if matchup['winner']:
                winner_name = matchup['winner'].split('-')[0]  # Extract winner name from ID
                winner_year = bracket["team_info"][matchup['winner']][2]
                winner = f" -> Winner: {winner_name} ({winner_year})"
            
            print(f"Matchup {i}: {team1} vs {team2}{conf}{winner}")



def get_round_matchups(bracket: Dict, round_num: int) -> List[Dict]:
    """
    Get all matchups from a specific round.
    
    Args:
        bracket: The bracket structure
        round_num: The round number to get matchups from
        
    Returns:
        List of matchups, where each matchup is a dictionary containing:
        - team1: First team name
        - team1_year: Year of first team
        - team2: Second team name
        - team2_year: Year of second team
        - conference: Conference name (or None for final round)
        - winner: Winner of the matchup (or None if not played)
        - winner_year: Year of winning team (or None if not played)
    """
    if round_num not in bracket["rounds"]:
        raise ValueError(f"Invalid round number: {round_num}")
    
    # For Round 2, ensure bye teams are properly placed
    if round_num == 2:
        bye_teams = bracket['rounds'][1]['teams_with_byes']
        matchups = bracket['rounds'][round_num]['matchups']
        teams_by_conf = {conf: [] for conf in bracket["conferences"]}
        
        # Group bye teams by conference
        for team, conf in bye_teams:
            teams_by_conf[conf].append(team)
        
        # Place bye teams in their conference's matchups if not already placed
        for i, matchup in enumerate(matchups):
            conf = matchup['conference']
            if conf and teams_by_conf[conf] and not matchup['team1']:
                matchup['team1'] = teams_by_conf[conf].pop(0)
    
    # Get base matchups
    matchups = bracket["rounds"][round_num]["matchups"]
    
    # Add year information to each matchup
    enhanced_matchups = []
    for matchup in matchups:
        enhanced_matchup = {
            "team1": matchup["team1"],
            "team1_year": bracket["team_info"][matchup["team1"]][2] if matchup["team1"] else None,
            "team2": matchup["team2"],
            "team2_year": bracket["team_info"][matchup["team2"]][2] if matchup["team2"] else None,
            "conference": matchup["conference"],
            "winner": matchup["winner"],
            "winner_year": bracket["team_info"][matchup["winner"]][2] if matchup["winner"] else None
        }
        enhanced_matchups.append(enhanced_matchup)
    
    return enhanced_matchups

    