import datetime
def holiday(year):
    """Japanese holiday @2016"""
    res, t = [], datetime.timedelta(1)
    sp = int(20.8431 + 0.242194 * (year - 1980) - (int)((year - 1980) / 4))
    au = int(23.2488 + 0.242194 * (year - 1980) - (int)((year - 1980) / 4))
    hs = ((1, 1), (1, -2), (2, 11), (3, sp), (4, 29), (5, 3), (5, 4), (5, 5),
          (7, -3), (8, 11), (9, -3), (9, au), (10, -2), (11, 3), (11, 23), (12, 23))
    for m, d in hs:
        dt = datetime.date(year, m, max(1, d))
        if d < 0:
            dt += ((7 - dt.weekday()) % 7 + 7 * (-1 - d)) * t
        if dt.weekday() == 6: dt += t
        while dt in res: dt += t
        res.append(dt)
    res = sorted(res)
    for d1, d2 in zip(res[:-1], res[1:]):
        if (d2 - d1).days == 2: res.append(d1 + datetime.timedelta(1))
    return set(res)
