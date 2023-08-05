"""Database module for tips.py"""

import json
import os
from . import dateapi

db_file = os.path.join(os.path.expanduser('~'), '.tips_db')

def _init():
    """Load db, create if nonexistent."""
    try:
        load()
    except IOError:
        file = open(db_file, 'w')
        file.close()
        load()

### API ###

#- File Actions -#

def load(): # Called by init() on import, part of API for posterity.
    """Get JSON data from db. Return {} if empty. Called on import."""
    global data

    with open(db_file, 'r') as file:
        try:
            data = json.load(file)
        except ValueError:
            data = {}

def save(): # To be used explicitly by tips.py when done.
    """Save data as JSON in db."""
    with open(db_file, 'w') as file:
        json.dump(data, file)

#- Retrieval -#

def get_value(date):
    """Get value for corresponding key. Return None if none."""
    try:
        return data[date]
    except KeyError:
        return None

def get_item(date):
    """Return 2-tuple with key, value pair. Return None if none."""
    try:
        return (date, data[date])
    except KeyError:
        return None

def get_range_dates(start, end):
    """Get range of dates, match in data, and return as a list."""
    range = dateapi.range(start, end)
    dates = [i for i in range if i in data.keys()]

    if dates == []:
        return None
    else:
        return dates

def get_range_values(start, end):
    """Get values under range of dates."""
    results = get_range(start, end)

    try:
        return zip(*results)[1]
    except TypeError:
        return None

def get_range(start, end):
    """Return range of date, amount pairs."""
    list = []
    dates = get_range_dates(start, end)

    if dates is None:
        return None
    else:
        for i in dates:
            list.append((i, get_value(i)))

        return list

def get_all():
    """Return generator with date, value pairs for every record in db."""
    for date, value in data.iteritems():
        yield (date, value)


#- Affect -#

def add(date, amount):
    """Increase by amount or set to amount if nonexistent."""
    if amount < 0:
        return False

    try:
        data[date] += amount
    except KeyError:
        data[date] = amount

def reduce(date, amount):
    """Reduce by amount. Return False if nonexistent or new amount less than 0."""
    try:
        if (data[date] - amount) < 0:
            return False
        elif (data[date] - amount) == 0:
            del data[date]
            return None
        else:
            data[date] -= amount
            return True
    except KeyError:
        return False

def replace(date, amount):
    """
    Replace value and create if nonexistent.
    Return False if less than 0, delete record if 0.
    """
    if amount > 0:
        data[date] = amount
        return True
    elif amount < 0:
        return False
    else:
        try:
            del data[date]
        except KeyError:
            pass

###---###

if __name__ != '__main__':
    _init()
