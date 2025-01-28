import pickle

from display import Display
from special import score, _passing_pct, _rushing_pct, _pressure_pct, _conversions_pct, _pass_fantasy_points, _run_fantasy_points, _pressure_fantasy_points, _conversions_fantasy_points, _penalties_fantasy_pints



class Stats:

    def __init__(self, year: int):
        self.year = year
        self.year_stats = self._load_stats()
    


    def _load_stats(self):
        with open(f"pickle/{self.year} NFL Team Stats.pkl", "rb") as pkl:
            return pickle.load(pkl)



    def apply_pct(self, stats: dict[str, int], stat_type: set[str]) -> None:
        for stat in stat_type:
            if stat == 'passing':
                _passing_pct(stats)
            elif stat == 'rushing':
                _rushing_pct(stats)
            elif stat == 'pressure':
                _pressure_pct(stats)
            elif stat == 'conversions':
                _conversions_pct(stats)



    def fantasy_points(self, stats: dict[str, int], stat_type: set[str]) -> None:
        stat_functions = {
            'passing': ('pass', _pass_fantasy_points),
            'rushing': ('rush', _run_fantasy_points),
            'pressure': ('pres', _pressure_fantasy_points),
            'conversions': ('conv', _conversions_fantasy_points),
            'penalties': ('pen_p', _penalties_fantasy_pints)
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
        gp = stats['gp'] if 'gp' in stats else 1
        stats[name] = ( ( stats['pts'] + stats['fantasy_points'] ) / 2 ) / gp



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
                off_pts = score(self.year_stats[team][week]['scoring'])
                def_pts = score(self.year_stats[opp][week]['scoring'])

                if off_pts > def_pts:
                    wins += 1
                elif def_pts > off_pts:
                    losses += 1
                else:
                    ties += 1
                
            stats[team]['record'] = {'gp': wins + losses + ties, 'wins': wins, 'losses': losses, 'ties': ties}



    def _in_week_range(self, week: int, start_week: int, end_week: int, custom_range: set[int]) -> bool:
        if start_week is not None and not week >= start_week:
            return False
        
        elif end_week is not None and not week <= end_week:
            return False
        
        elif custom_range is not None and int(week) not in custom_range:
            return False
        
        else:
            return True



    def _which_stats(self, team: str, week: int, side_of_the_ball: str, stats: dict, per_week = False) -> list[str]:
        if side_of_the_ball is None:
            look_at = [team, self.year_stats[team][week]['opp']]

            if not per_week and 'offense' not in stats[team]:
                    stats[team]['offense'] = {} 
                    stats[team]['defense'] = {}

        elif side_of_the_ball == 'offense':
            look_at = [team]

            if not per_week and 'offense' not in stats[team]:
                stats[team]['offense'] = {}

        else:
            look_at = [self.year_stats[team][week]['opp']]

            if not per_week and 'defense' not in stats[team]:
                stats[team]['defense'] = {}
        
        return look_at



    def _add_stats(self, team: str, look_at: list[str], week: int, stat_type: set[str]) -> dict:
        stats = {}

        for current_team in look_at:
            key = 'offense' if current_team == team else 'defense'
            stats[key] = {}
            
            for stat_catagorie in stat_type:

                if stat_catagorie == 'opp':
                    continue

                for stat, value in self.year_stats[current_team][week][stat_catagorie].items():
                    stats[key][stat] = value
        
        return stats



    def combine_stats(self, returned_stats: dict, week_stats: dict) -> None:
        for side in week_stats:
            for stat, value in week_stats[side].items():

                if stat not in returned_stats[side]:
                    returned_stats[side][stat] = value
                else:
                    returned_stats[side][stat] += value



    def _process_stats(self, stats, stat_type, side):
        self.apply_pct(stats, stat_type)
        self.fantasy_points(stats, stat_type)
        stats['pts'] = score(stats)
        self.simple_team_rating(stats, side)


        
    def _apply_special_stats(self, returned_stats: dict, stat_type: set[str], per_week = False) -> None:
        for team, team_stats in returned_stats.items():
            if per_week:
                for week, week_stats in team_stats.items():
                    for side, stats in week_stats.items():
                        self._process_stats(stats, stat_type, side)
            else:
                for side, stats in team_stats.items():
                    self._process_stats(stats, stat_type, side)


    def grab_stats(self, teams: list[str] = None, side_of_the_ball: str = None, stat_type: set[str] = None, start_week: int = None, end_week: int = None, custom_range: set[int] = None, apply_extra: bool = True) -> dict[str, dict[str, int]]:
        teams = teams if teams is not None else list(self.year_stats.keys())
        stat_type = stat_type if stat_type is not None else self.year_stats[teams[0]]['2'].keys()
        returned_stats = {}

        for team in teams:
            if start_week is not None:
                max_week = max(list(map(int, self.year_stats[team].keys())))
                if start_week > max_week:
                    continue

            returned_stats[team] = {}
            game_count = 0
            for week in self.year_stats[team]:
                
                if not self._in_week_range(int(week), start_week, end_week,custom_range):
                    continue
                
                game_count += 1
                look_at = self._which_stats(team, week, side_of_the_ball, returned_stats)

                week_stats = self._add_stats(team, look_at, week, stat_type)

                self.combine_stats(returned_stats[team], week_stats)

            if 'offense' in returned_stats[team]:
                returned_stats[team]['offense']['gp'] = game_count 
            
            if 'defense' in returned_stats[team]:
                returned_stats[team]['defense']['gp'] = game_count

        if apply_extra:
            self._apply_special_stats(returned_stats, stat_type)
        
        if side_of_the_ball is None:
            self.add_records(returned_stats.keys(), returned_stats, start_week, end_week, custom_range)

        return returned_stats



    def grab_stats_per_week(self, teams: list[str] = None, side_of_the_ball: str = None, stat_type: set[str] = None, start_week: int = None, end_week: int = None, custom_range: set[int] = None, apply_extra: bool = False) -> dict[int, list[int]]:
        teams = [teams] if teams is not None else list(self.year_stats.keys())
        if len(teams[0]) > 3:
            teams[0] = teams[0][:3]

        stat_type = stat_type if stat_type is not None else self.year_stats[teams[0]]['2'].keys()
        returned_stats = {}
        per_week = True

        for team in teams:
            if start_week is not None:
                max_week = max(list(map(int, self.year_stats[team].keys())))
                if start_week > max_week:
                    continue
            
            returned_stats[team] = {}
            for week in self.year_stats[team]:
                
                if not self._in_week_range(int(week), start_week, end_week,custom_range):
                    continue
                
                look_at = self._which_stats(team, week, side_of_the_ball, returned_stats, per_week)

                returned_stats[team][week] = self._add_stats(team, look_at, week, stat_type)
        
        if apply_extra:
            self._apply_special_stats(returned_stats, stat_type, per_week)
        
        return returned_stats

    

def team_rankins(start_year: int, end_year: int, start_week: int, end_week: int) -> None:
    teams = None
    side_of_the_ball = None
    stat_type = { 'passing', 'rushing', 'pressure', 'scoring' }
    custom_range = None
    total_stats = {}

    for year in range(start_year, end_year + 1):
        stats = Stats(year)

        returned_stats = stats.grab_stats(teams=teams, side_of_the_ball=side_of_the_ball, stat_type=stat_type, start_week=start_week, end_week=end_week, custom_range=custom_range)
        total_stats[year] = returned_stats
    
    big_list = []
    view = Display()
    for year in total_stats:
        big_list = big_list + view.create_team_rankings(total_stats[year], side_of_the_ball, year)

    big_list.sort(key=lambda x: x[6], reverse=True)
    view.display_team_rankings(big_list)



if __name__ == "__main__":
    year = 2024
    team_rankins(2021, 2024, 1, 22)