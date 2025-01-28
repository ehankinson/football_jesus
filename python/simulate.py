import random
import numpy as np 
import multiprocessing as mp
from functools import partial
from tqdm import tqdm

from stats import Stats
from special import score


class Simulate():


    def __init__(self):
        self.teams = {}



    def _in_teams(self, team: str, games: Stats, side: bool):
        if team not in self.teams:
            self.teams[team] = {'offense': {}, 'defense': {}}

        key = 'offense' if side else 'defense'
        small_key = 'off' if side else 'def'

        if len(self.teams[team][key]) == 0:
            stats, pct, keys = self.create_histogram(games, key, team)
            self.teams[team][key] = {f"{small_key}_stats": stats, f"{small_key}_pct": pct, f"{small_key}_keys": keys}



    def search(self, ranks: list[float], position: float):
        if position < ranks[0]:
            return ranks[0]
        
        l, r = 0, len(ranks) - 1

        while l <= r:
            m = (l + r) // 2

            if ranks[m - 1] <= position <= ranks[m]:
                return ranks[m]
            elif ranks[m] > position:
                r = m - 1
            elif ranks[m] < position:
                l = m + 1



    def find(self, pcts: list[float], value: float):
        for index, pct in enumerate(pcts):
            if value < pct:
                return index



    def histogram_math(self, ranks: list[float]):
        # Calculate bin width using Freedman-Diaconis rule
        bin_width = 2 * (np.percentile(ranks, 75) - np.percentile(ranks, 25)) * (len(ranks) ** (-1/3))
        
        # Calculate bin edges
        data_min = min(ranks)
        data_max = max(ranks)
        
        # Create bin edges from min to max using the calculated width
        bin_edges = np.arange(data_min, data_max + bin_width, bin_width)
        
        # Count items in each bin
        counts, _ = np.histogram(ranks, bins=bin_edges)
        
        # Create a dictionary mapping each bin range to its count
        bin_counts = {}
        total_count = 0
        for i in range(len(counts)):
            bin_range = bin_edges[i + 1]
            total_count += counts[i]
            bin_counts[bin_range] = total_count / len(ranks)
        
        return bin_counts



    def create_histogram(self, league_stats: Stats, side_of_the_ball: str, team: str = None):
        score = 'sors' if side_of_the_ball == 'offense' else 'sdrs'
        stats_per_week = league_stats.grab_stats_per_week(team, side_of_the_ball, apply_extra=True)
        ranks = []

        for team in stats_per_week:
            for week in stats_per_week[team]:
                ranks.append(stats_per_week[team][week][side_of_the_ball][score])
        
        # Get bin counts
        bin_distribution = self.histogram_math(ranks)
        
        pct = list(bin_distribution.values())
        keys = list(bin_distribution.keys())

        for team in stats_per_week:
            for week in stats_per_week[team]:
                key = self.search(list(bin_distribution.keys()), stats_per_week[team][week][side_of_the_ball][score])

                if not isinstance(bin_distribution[key], list):
                    bin_distribution[key] = [week]
                else:
                    bin_distribution[key].append(week)

        return bin_distribution, pct, keys



    def select_game(self, stats: dict, percentages: list, keys: list, side: bool):
        rng = random.random() if side else 1 - random.random()
        idx = self.find(percentages, rng)
        key = keys[idx]

        if not side:
            rng = 1 - rng

        return random.choice(stats[key]), rng




    def game_stats(self, off_team: str, off_games: dict, def_team: str, def_games: dict):
        self._in_teams(off_team, off_games, True)
        self._in_teams(def_team, def_games, False)

        off_game, off_rng = self.select_game(self.teams[off_team]['offense']['off_stats'], self.teams[off_team]['offense']['off_pct'], self.teams[off_team]['offense']['off_keys'], True)
        def_game, def_rng = self.select_game(self.teams[def_team]['defense']['def_stats'], self.teams[def_team]['defense']['def_pct'], self.teams[def_team]['defense']['def_keys'], False)

        total_rng = off_rng + def_rng
        nor_rng = 1 / total_rng
        off_rng = off_rng * nor_rng
        def_rng = def_rng * nor_rng

        off_game_stats = off_games.year_stats[off_team][off_game]
        def_game_stats = def_games.year_stats[def_games.year_stats[def_team][def_game]['opp']][def_game]

        return_stats = {}
        for key in off_game_stats:
            if key == 'opp':
                continue

            return_stats[key] = {}
            for stat in off_game_stats[key]:
                return_stats[key][stat] = off_game_stats[key][stat] * off_rng + def_game_stats[key][stat] * def_rng
        
        return_stats['scoring']['pts'] = score(return_stats['scoring'])
        return return_stats



    def simulate_game(self, home_team, home_stats, away_team, away_stats):
        home_team_game = self.game_stats(home_team, home_stats, away_team, away_stats)
        away_team_game = self.game_stats(away_team, away_stats, home_team, home_stats)

        home_pts = home_team_game['scoring']['pts']
        away_pts = away_team_game['scoring']['pts']

        if home_pts > away_pts:
            return 1
        elif home_pts < away_pts:
            return -1
        else:
            return 0



    def simulate_games(self, home_team, home_stats, away_team, away_stats, game_played):
        home_wins = 0
        away_wins = 0
        ties = 0
        
        for _ in tqdm(range(game_played), desc=f"Simulating {home_team} vs {away_team}", leave=False):
            winner = self.simulate_game(home_team, home_stats, away_team, away_stats)

            if winner > 0:
                home_wins += 1
            elif winner < 0:
                away_wins += 1
            else:
                ties += 1
        
        if home_wins > away_wins:
            return home_team
        elif away_wins > home_wins:
            return away_team
        else:
            return "TIED"