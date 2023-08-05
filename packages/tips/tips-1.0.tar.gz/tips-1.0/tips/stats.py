"""Stats module for tips.py"""

from collections import OrderedDict
from . import db
from . import dateapi

TEXT_1 = """{6}
Total:                            Average per day:

Past week     - {0:<18}Past week     - {3:<18}
Past 30 days  - {1:<18}Past 30 days  - {4:<18}
Past year     - {2:<18}Past year     - {5:<18}
All time      - {7:<18}All time      - {8:<18}
{6}"""

TEXT_2 = """{0}
Average per weekday:

Past week ---                     Past 30 days ---

Mon - {1:<28}Mon - {8}
Tue - {2:<28}Tue - {9}
Wed - {3:<28}Wed - {10}
Thu - {4:<28}Thu - {11}
Fri - {5:<28}Fri - {12}
Sat - {6:<28}Sat - {13}
Sun - {7:<28}Sun - {14}"""

TEXT_3 = """
Past year ---                     All time ---

Mon - {1:<28}Mon - {8}
Tue - {2:<28}Tue - {9}
Wed - {3:<28}Wed - {10}
Thu - {4:<28}Thu - {11}
Fri - {5:<28}Fri - {12}
Sat - {6:<28}Sat - {13}
Sun - {7:<28}Sun - {14}"""

def total(days):
    """Sum values under range of days. Pass 'all_time' for all time."""
    if days == 'all_time':
        results = [value for date, value in db.get_all()]
    else:
        results = db.get_range_values(dateapi.today(), dateapi.time_ago(days-1))

    return round(sum(results), 2)

def average(days):
    """Average values under range of days. Pass 'all_time' for all time."""
    if days == 'all_time':
        results = [value for date, value in db.get_all()]
    else:
        results = db.get_range_values(dateapi.today(), dateapi.time_ago(days))

    return round(sum(results) / len(results), 2)

def get_weekdays(days):
    """
    Return pair of (total, entries) for each day of the week under range of days.
    """
    weekdays = OrderedDict({
        1: [0, 0], # 1[0] accumulates value, 1[1] accumulates instances of weekday.
        2: [0, 0],
        3: [0, 0],
        4: [0, 0],
        5: [0, 0],
        6: [0, 0],
        7: [0, 0],
    })

    if days == 'all_time':
        results = [(dateapi.weekday(date), value) for date, value in db.get_all()]
    else:
        days -= 1
        results = db.get_range(dateapi.today(), dateapi.time_ago(days))
        results = [(dateapi.weekday(date), value) for date, value in results]

    for day, value in results:
        weekdays[day][0] += value
        weekdays[day][1] += 1

    return weekdays

def average_weekday(days):
    """
    Average values per weekday under range of days.
    Pass 'all_time' for all time.
    """
    output = []
    weekdays = get_weekdays(days)

    for day in weekdays.iterkeys():
        try:
            weekdays[day] = weekdays[day][0] / weekdays[day][1]
        except ZeroDivisionError:
            weekdays[day] = 0

    for day, value in weekdays.iteritems():
        output.append(round(value, 2))

    return output


def separator(initial, values):
    """Generate separator based on inital value, plus collection of values."""
    sep = "-" * (initial + max([len(str(i)) for i in values]))
    return sep

def print_stats():
    """Print table of stats."""
    sep_1 = separator(50, (average(7), average(30), average(365), average('all_time')))

    print TEXT_1.format(total(7), total(30), total(365),
                        average(7), average(30), average(365), sep_1,
                        total('all_time'), average('all_time'))

    average_weekday_1 = average_weekday(7)
    average_weekday_1.extend(average_weekday(30))

    print TEXT_2.format(sep_1, *average_weekday_1)

    average_weekday_2 = average_weekday(365)
    average_weekday_2.extend(average_weekday('all_time'))

    print TEXT_3.format('', *average_weekday_2)

    print sep_1
