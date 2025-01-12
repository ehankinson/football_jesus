import csv
import pickle

year = 2023
path = f"csv/{year} NFL Team Stats.csv"

year_stats = {}
PASSING = { 'cmp': 16, 'p_att': 17, 'p_yds': 20, 'p_td': 21, 'int': 22, 'p_1d': 54 }
RUSHING = { 'r_att': 34, 'r_yds': 35, 'r_td': 37, 'fum': ( 43, 22 ), 'r_1d': 53 }
PRESSURE = { 'sk': 26, 's_yds': 27 }
CONVERSIONS = { '3da': 56, '3dc': 57, '4da': 59, '4dc': 60 }
PENALTIES = { 'pen': 46, 'yds': 47, 'pen_1d': 55 }
SCORING = { 't_td': 62, 'xpa': 63, 'xpm': 64, 'fga': 65, 'fgm': 66, '2pa': 67, '2pm': 68, 'sfty': 69, 'krtd': 70, 'prtd': 71, 'inttd': 72, 'frtd': 73, 'otd': 74 }

KEYS = {
    'passing': PASSING,
    'rushing': RUSHING,
    'pressure': PRESSURE,
    'conversions': CONVERSIONS,
    'penalties': PENALTIES,
    'scoring': SCORING
}

 
with open(path, 'r') as f:
    reader = csv.reader(f)

    for row in reader:
        
        if row[1] == "Team":
            continue
        
        team = row[1]
        if team not in year_stats:
            year_stats[team] = {}
        
        week = row[12]
        opponent = row[14]
        if week not in year_stats[team]:
            year_stats[team][week] = {}
            year_stats[team][week]['opp'] = opponent

        for key in KEYS:
            year_stats[team][week][key] = {}

            for stat, value in KEYS[key].items():

                if isinstance(value, tuple):
                    year_stats[team][week][key][stat] = int(row[value[0]]) - int(row[value[1]])
                else:
                    year_stats[team][week][key][stat] = int(row[value])


with open(f"pickle/{year} NFL Team Stats.pkl", "wb") as pkl:
    pickle.dump(year_stats, pkl)