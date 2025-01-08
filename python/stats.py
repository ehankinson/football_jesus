import pickle



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
    


    def qbr(self, cmp: int, att: int, yds: int, td: int, int: int):
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



    def grab_stats(self, teams: list[str] = None, side_of_the_ball: str = None, stat_type: set[str] = None, start_week: int = None, end_week: int = None, custom_range: set[int] = None) -> dict[str, dict[str, int]]:
        teams = teams if teams is not None else self.year_stats.keys()
        returned_stats = {}

        for team in teams:
            returned_stats[team] = {}

            for week in self.year_stats[team]:
                
                if start_week is not None and end_week is not None and not start_week <= int(week) <= end_week:
                    continue
                
                elif custom_range is not None and int(week) not in custom_range:
                    continue

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

        for team in returned_stats:
            for side in returned_stats[team]:
                self.apply_pct(returned_stats[team][side], stat_type)


        return returned_stats



if __name__ == "__main__":
    year = 2024
    stats = Stats(year)

    teams = [
        'CIN',
        'BAL',
        'CAR',
        'DET',
        'TAM',
        'PHI'
    ]

    side_of_the_ball = 'defense'
    stat_type = {
        'passing',
        'rushing',
        'conversions'
    }
    start_week = None
    end_week = None
    custom_range = None

    returned_stats = stats.grab_stats(teams=teams, side_of_the_ball=side_of_the_ball, stat_type=stat_type, start_week=start_week, end_week=end_week, custom_range=custom_range)
    a =  5

