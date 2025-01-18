import numpy as np

from stats import Stats



def search(percentages: list[float], position: float):
    l, r = 0, len(percentages) - 1

    while l < r:
        m = (l + r) // 2
        if percentages[m] > position:
            r = m - 1
        elif percentages[m] < position:
            l = m + 1
        else:
            return position



def histogram_math(ranks: list[float]):
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



def create_histogram(league_stats: Stats, team: str = None):
    stats_per_week = league_stats.grab_stats_per_week(team, side_of_the_ball='offense', apply_extra=True)
    ranks = []

    for team in stats_per_week:
        for week in stats_per_week[team]:
            ranks.append(stats_per_week[team][week]['offense']['sors'])
    
    # Get bin counts
    bin_distribution = histogram_math(ranks)
    
    percentages = list(bin_distribution.values())

    for team in stats_per_week:
        for week in stats_per_week[team]:
            key = search(bin_distribution.keys(), stats_per_week[team][week]['offense']['sors'])

            if not isinstance(bin_distribution[key], list):
                bin_distribution[key] = [stats_per_week[team][week]['offense']['sors']]
            else:
                bin_distribution[key].append(stats_per_week[team][week]['offense']['sors'])

    return bin_distribution



if __name__ == "__main__":
    away_team = 'BUF'
    away_year = 2024
    away_stats = Stats(away_year)

    home_team = 'BAL'
    home_year = 2024
    home_stats = Stats(away_year)

    if away_year == home_year:
        home_league_stats = create_histogram(home_stats)
        away_league_stats = home_league_stats
    else:
        home_league_stats = create_histogram(home_stats)
        away_league_stats = create_histogram(away_stats)

    home_team_stats = create_histogram(home_stats, home_team)
    away_team_stats = create_histogram(away_stats, away_team)

    a = 5
        
