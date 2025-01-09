import pickle
import pandas as pd



class Stats:

    def __init__(self, year: int):
        self.year = year
        self.year_stats = self._load_stats()
        self.PCT = {

            'conversions': [ '3d%', '4d%' ],
        }
    


    def _load_stats(self):
        with open(f"pickle/{self.year} NFL Team Stats.pkl", "rb") as pkl:
            return pickle.load(pkl)
    


    def pct(self, numerator: int, denominator: int) -> float:
        return numerator / denominator * 100
    


    def per_att(self, stat: int, att: int) -> float:
        return stat / att
    


    def qbr(self, cmp: int, att: int, yds: int, td: int, int: int) -> float:
        a = ( ( cmp / att * 100 ) - 30 ) * 0.05
        b = ( ( yds / att ) - 3 ) * 0.25
        c = ( td / att * 100 ) * 0.2
        d = 2.375 - ( ( int / att * 100) * 0.25 )
        
        a = max(0, min(a, 2.375))
        b = max(0, min(b, 2.375))
        c = max(c, 2.375)
        d = max(0, d)

        rate = ( ( a + b + c + d ) / 6 ) * 100
        return rate
    



    def _pass_fantasy_points(self, stats: dict[str, int]) -> float:
        return (
            stats['p_yds'] * 0.05 +
            stats['p_td'] * 6 +
            stats['int'] * -6 +
            stats['p_1d'] * 0.5
        )



    def _run_fantasy_points(self, stats: dict[str, int]) -> float:
        return (
            stats['r_yds'] * 0.1 +
            stats['r_td'] * 6 + 
            stats['fum'] * -6 +
            stats['r_1d'] * 0.5
        )



    def _pressure_fantasy_points(self, stats: dict[str, int]) -> float:
        return (
            stats['sk'] * -2 +
            stats['s_yds'] * -0.05
        )



    def _conversions_fantasy_points(self, stats: dict[str, int]) -> float:
        return (
            stats['3dc'] * 0.2 +
            stats['4dc'] * 2
        )
    


    def _penalties_fantasy_pints(self, stats: dict[str, int]) -> float:
        return (
            stats['pen'] * -0.5 +
            stats['p_yds'] * -0.01 +
            stats['p_1d'] * 0.25
        )



    def score(self, stats: dict[str, int]) -> int:
        return (
            stats['t_td'] * 6 +
            stats['xpm'] * 1 +
            stats['fgm'] * 3 +
            stats['2pm'] * 2 +
            stats['sfty'] * 2 
        )
    


    def _passing_pct(self, stats: dict[str, int]) -> None:
        att = stats['p_att']
        stats['cmp%'] = self.pct(stats['cmp'], att)
        stats['p_y/a'] = self.per_att(stats['p_yds'], att)
        stats['p_td%'] = self.pct(stats['p_td'], att)
        stats['p_int%'] = self.pct(stats['int'], att)
        stats['p_1d%'] = self.pct(stats['p_1d'], att)
        stats['rate'] = self.qbr(stats['cmp'], att, stats['p_yds'], stats['p_td'], stats['int'])



    def _rushing_pct(self, stats: dict[str, int]) -> None:
        att = stats['r_att']
        stats['r_y/a'] = self.per_att(stats['r_yds'], att)
        stats['r_td%'] = self.pct(stats['r_td'], att)
        stats['fum%'] = self.pct(stats['fum'], att)
        stats['r_1d%'] = self.pct(stats['r_1d'], att)



    def _pressure_pct(self, stats: dict[str, int]) -> None:
        stats['y/s'] = self.per_att(stats['s_yds'], stats['sk'])
        stats['sk%'] = self.pct(stats['sk'], stats['p_att'])



    def _conversions_pct(self, stats: dict[str, int]) -> None:
        stats['3d%'] = self.pct(stats['3dc'], stats['3da'])
        stats['4d%'] = self.pct(stats['4dc'], stats['4da'])



    def apply_pct(self, stats: dict[str, int], stat_type: set[str]) -> None:
        for stat in stat_type:
            if stat == 'passing':
                self._passing_pct(stats)
            elif stat == 'rushing':
                self._rushing_pct(stats)
            elif stat == 'pressure':
                self._pressure_pct(stats)
            else:
                self._conversions_pct(stats)



    def fantasy_points(self, stats: dict[str, int], stat_type: set[str]) -> None:
        stat_functions = {
            'passing': ('pass', self._pass_fantasy_points),
            'rushing': ('rush', self._run_fantasy_points),
            'pressure': ('pres', self._pressure_fantasy_points),
            'conversions': ('conv', self._conversions_fantasy_points),
            'penalties': ('pen_p', self._penalties_fantasy_pints)
        }

        total = 0
        for stat in stat_type:
            if stat in stat_functions:
                stat_key, func = stat_functions[stat]
                score = func(stats)
                stats[stat_key] = stats.get(stat_key, 0) + score
                total += score
        
        stats['fantasy_points'] = total
    


    def simple_team_rating(self, stats: dict[str, int], side_of_the_ball: str) -> None:
        name = 'sors' if side_of_the_ball == 'offense' else 'sdrs'
        stats[name] = ( ( stats['pts'] + stats['fantasy_points'] ) / 2 ) / stats['gp']



    def add_records(self, teams: list[str], stats: dict, start_week: int = None, end_week: int = None, custom_range: set[int] = None) -> None:
        for team in teams:
            
            wins = 0
            losses = 0
            ties = 0

            for week in self.year_stats[team]:
                
                if start_week is not None and end_week is not None and not start_week <= int(week) <= end_week:
                    continue
                
                elif custom_range is not None and int(week) not in custom_range:
                    continue
                
                opp = self.year_stats[team][week]['opp']
                off_pts = self.score(self.year_stats[team][week]['scoring'])
                def_pts = self.score(self.year_stats[opp][week]['scoring'])

                if off_pts > def_pts:
                    wins += 1
                elif def_pts > off_pts:
                    losses += 1
                else:
                    ties += 1
                
            stats[team]['record'] = {'gp': wins + losses + ties, 'wins': wins, 'losses': losses, 'ties': ties}



    def grab_stats(self, teams: list[str] = None, side_of_the_ball: str = None, stat_type: set[str] = None, start_week: int = None, end_week: int = None, custom_range: set[int] = None) -> dict[str, dict[str, int]]:
        teams = teams if teams is not None else self.year_stats.keys()
        returned_stats = {}

        for team in teams:
            returned_stats[team] = {}

            game_count = 0
            for week in self.year_stats[team]:
                
                if start_week is not None and end_week is not None and not start_week <= int(week) <= end_week:
                    continue
                
                elif custom_range is not None and int(week) not in custom_range:
                    continue
                
                game_count += 1
                if side_of_the_ball is None:
                    look_at = [team, self.year_stats[team][week]['opp']]

                    if 'offense' not in returned_stats[team]:
                        returned_stats[team]['offense'] = {} 
                        returned_stats[team]['defense'] = {}

                elif side_of_the_ball == 'offense':
                    look_at = [team]

                    if 'offense' not in returned_stats[team]:
                        returned_stats[team]['offense'] = {}

                else:
                    look_at = [self.year_stats[team][week]['opp']]

                    if 'defense' not in returned_stats[team]:
                        returned_stats[team]['defense'] = {}

                for current_team in look_at:
                    stat_type = stat_type if stat_type is not None else self.year_stats[current_team][week].keys()
                    
                    for stat_catagorie in stat_type:

                        if stat_catagorie == 'opp':
                            continue
                        
                        key = 'offense' if current_team == team else 'defense'

                        for stat, value in self.year_stats[current_team][week][stat_catagorie].items():
                            if stat not in returned_stats[team][key]:
                                returned_stats[team][key][stat] = 0
                            
                            returned_stats[team][key][stat] += value

            if 'offense' in returned_stats[team]:
                returned_stats[team]['offense']['gp'] = game_count 
            
            if 'defense' in returned_stats[team]:
                returned_stats[team]['defense']['gp'] = game_count

        for team in returned_stats:
            for side in returned_stats[team]:
                self.apply_pct(returned_stats[team][side], stat_type)
                self.fantasy_points(returned_stats[team][side], stat_type)
                returned_stats[team][side]['pts'] = self.score(returned_stats[team][side])
                self.simple_team_rating(returned_stats[team][side], side)
        
        if side_of_the_ball is None:
            self.add_records(teams, returned_stats, start_week, end_week, custom_range)

        return returned_stats
    


    def display_team_rankings(self, stats: dict[str, dict[str, int]], side_of_the_ball: str) -> pd.DataFrame:
        final_results = []
        if side_of_the_ball is not None:
            print("Cannot print this section since not all sides are present")
            return
        else:
            for team in stats:
                curr = []
                curr.append(team)  # Team name
                curr.append(self.year)  # Year
                curr.append(stats[team]['record']['wins'])
                curr.append(stats[team]['record']['losses'])
                curr.append(stats[team]['record']['ties'])
                curr.append(self.pct(stats[team]['record']['wins'], (stats[team]['record']['wins'] + stats[team]['record']['losses'] + stats[team]['record']['ties'])))
                curr.append(stats[team]['offense']['sors'] - stats[team]['defense']['sdrs'])  # SORS-SDRS
                curr.append(stats[team]['offense']['sors'])  # Offense SORS
                curr.append(stats[team]['defense']['sdrs'])  # Defense SDRS
                curr.append(stats[team]['offense']['fantasy_points'] - stats[team]['defense']['fantasy_points'])  # SORS-SDRS
                curr.append(stats[team]['offense']['fantasy_points'])  # Offense Fantasy Points
                curr.append(stats[team]['defense']['fantasy_points'])  # Defense Fantasy Points
                curr.append(stats[team]['offense']['pts'] - stats[team]['defense']['pts'])  # SORS-SDRS
                curr.append(stats[team]['offense']['pts'])  # Offense Points
                curr.append(stats[team]['defense']['pts'])  # Defense Points

                final_results.append(curr)

            # Sort results by the 3rd element (SORS - SDRS) in descending order
            final_results.sort(key=lambda x: x[6], reverse=True)

            # Convert to Pandas DataFrame
            columns = [
                "Team", "Year", "Wins", "Losses", "Ties", "Win%", "Team STRS", "Offense SORS", "Defense SDRS", 'Diff',
                "Off FP", "Def FP", 'NP',
                "PF", "PA"
            ]
            df = pd.DataFrame(final_results, columns=columns)
            
            return df
    


    def display_side_of_the_ball_rankings(self, stats: dict[str, dict[str, int]], side_of_the_ball: str):
        final_results = []
        key = 'sors' if side_of_the_ball == 'offense' else 'sdrs'

        for team in stats:
            short = stats[team][side_of_the_ball]
            curr = []
            curr.append(team)
            curr.append(self.year)
            curr.append(short['gp'])
            curr.append(short['pts'])
            curr.append(short['p_yds'] + short['r_yds'])
            curr.append(short['cmp'])
            curr.append(short['p_att'])
            curr.append(short['p_yds'])
            curr.append(short['p_td'])
            curr.append(short['int'])
            curr.append(short['p_1d'])
            curr.append(short['sk'])
            curr.append(short['s_yds'])
            curr.append(short['r_att'])
            curr.append(short['r_yds'])
            curr.append(short['r_td'])
            curr.append(short['fum'])
            curr.append(short['r_1d'])
            curr.append(short['3d%'])
            curr.append(short['4d%'])
            curr.append(short['pen'])
            curr.append(short['yds'])
            curr.append(short['fantasy_points'])
            curr.append(short[key])
            final_results.append(curr)

        length = len(final_results[0]) - 1
        if side_of_the_ball == 'offense':
            final_results.sort(key=lambda x: x[length], reverse=True)
        else:
            final_results.sort(key=lambda x: x[length])

        columns = [
                "Team", "Year", "GP", "PTS", "YDS", "CMP", "ATT", "YDS", "TD", 'INT',
                "1D", "SK", 'YDS', 'ATT', 'YDS', 'TD', 'FUM', '1D', '3D%', '4D%', 'PEN', 'YDS',
                "FP", key
        ]
        df = pd.DataFrame(final_results, columns=columns)
        
        return df




if __name__ == "__main__":
    year = 2024
    stats = Stats(year)

    teams = None

    side_of_the_ball = None
    stat_type = None
    start_week = 1
    end_week = 18
    custom_range = None

    returned_stats = stats.grab_stats(teams=teams, side_of_the_ball=side_of_the_ball, stat_type=stat_type, start_week=start_week, end_week=end_week, custom_range=custom_range)
    # team_rankings = stats.display_team_rankings(returned_stats, side_of_the_ball)
    off_rankings = stats.display_side_of_the_ball_rankings(returned_stats, 'defense')

    from IPython.display import display
    display(off_rankings)

