def pct(numerator: int, denominator: int) -> float:
        if denominator == 0:
            return 0
        
        return numerator / denominator * 100
    


def per_att(stat: int, att: int) -> float:
    if att == 0:
        return 0
    
    return stat / att



def qbr(cmp: int, att: int, yds: int, td: int, int: int) -> float:
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



def _pass_fantasy_points(stats: dict[str, int]) -> float:
    return (
        stats['p_yds'] * 0.05 +
        stats['p_td'] * 6 +
        stats['int'] * -6 +
        stats['p_1d'] * 0.5
    )



def _run_fantasy_points(stats: dict[str, int]) -> float:
    return (
        stats['r_yds'] * 0.1 +
        stats['r_td'] * 6 + 
        stats['fum'] * -6 +
        stats['r_1d'] * 0.5
    )



def _pressure_fantasy_points(stats: dict[str, int]) -> float:
    return (
        stats['sk'] * -2 +
        stats['s_yds'] * -0.05
    )



def _conversions_fantasy_points(stats: dict[str, int]) -> float:
    return (
        stats['3dc'] * 0.2 +
        stats['4dc'] * 2
    )



def _penalties_fantasy_pints(stats: dict[str, int]) -> float:
    return (
        stats['pen'] * -0.5 +
        stats['p_yds'] * -0.01 +
        stats['p_1d'] * 0.25
    )



def score(stats: dict[str, int]) -> int:
    return (
        stats['t_td'] * 6 +
        stats['xpm'] * 1 +
        stats['fgm'] * 3 +
        stats['2pm'] * 2 +
        stats['sfty'] * 2 
    )



def _passing_pct(stats: dict[str, int]) -> None:
    att = stats['p_att']
    stats['cmp%'] = pct(stats['cmp'], att)
    stats['p_y/a'] = per_att(stats['p_yds'], att)
    stats['p_td%'] = pct(stats['p_td'], att)
    stats['p_int%'] = pct(stats['int'], att)
    stats['p_1d%'] = pct(stats['p_1d'], att)
    stats['rate'] = qbr(stats['cmp'], att, stats['p_yds'], stats['p_td'], stats['int'])



def _rushing_pct(stats: dict[str, int]) -> None:
    att = stats['r_att']
    stats['r_y/a'] = per_att(stats['r_yds'], att)
    stats['r_td%'] = pct(stats['r_td'], att)
    stats['fum%'] = pct(stats['fum'], att)
    stats['r_1d%'] = pct(stats['r_1d'], att)



def _pressure_pct(stats: dict[str, int]) -> None:
    stats['y/s'] = per_att(stats['s_yds'], stats['sk'])
    stats['sk%'] = pct(stats['sk'], stats['p_att'])



def _conversions_pct(stats: dict[str, int]) -> None:
    stats['3d%'] = pct(stats['3dc'], stats['3da'])
    stats['4d%'] = pct(stats['4dc'], stats['4da'])