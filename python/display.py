import pandas as pd

from IPython.display import display


class Display:


    def create_team_rankings(self, stats: dict[str, dict[str, int]], side_of_the_ball: str, year: int) -> pd.DataFrame:
        final_results = []
        if side_of_the_ball is not None:
            print("Cannot print this section since not all sides are present")
            return
        else:
            for team in stats:
                curr = []
                curr.append(team)  # Team name
                curr.append(year)  # Year
                curr.append(stats[team]['record']['wins'])
                curr.append(stats[team]['record']['losses'])
                curr.append(stats[team]['record']['ties'])
                curr.append(pct(stats[team]['record']['wins'], (stats[team]['record']['wins'] + stats[team]['record']['losses'] + stats[team]['record']['ties'])))
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
            return final_results.sort(key=lambda x: x[6], reverse=True)
    


    def display_team_rankings(self, final_results: list[list]) -> None:
        columns = [
                "Team", "Year", "Wins", "Losses", "Ties", "Win%", "Team STRS", "Offense SORS", "Defense SDRS", 'Diff',
                "Off FP", "Def FP", 'NP',
                "PF", "PA"
        ]
        df = pd.DataFrame(final_results, columns=columns)
        display(df)



    def display_side_of_the_ball_rankings(self, stats: dict[str, dict[str, int]], side_of_the_ball: str):
        final_results = []
        key = 'sors' if side_of_the_ball == 'offense' else 'sdrs'

        for team in stats:
            short = stats[team][side_of_the_ball]
            curr = []
            curr.append(team)
            curr.append(year)
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