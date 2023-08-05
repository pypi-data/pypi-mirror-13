#!/usr/bin/env python2

"""
test_gen_db.py - enter random values between range of dates into tips.py db for testing.

Usage: test_gen_db.py <from> <to> <value_range>

Arguments:
    from - Date in format YYYY-MM-DD or by amount of time ago e.g. 1d3w2y or 4d or 2w1d.
    to - Date in format YYYY-MM-DD or by amount of time ago e.g. 1d3w2y or 4d or 2w1d.

    value_range - Possible range for values entered into db. e.g. 60.

Example:
    ./test_gen_db.py 30d 0d 30 - Will enter random values between 1 and 50
                                 for the past 30 days.
"""

from random import randint
from sys import argv
from . import db
from . import dateapi

def generate(from_date, to_date, in_range):
    result = dateapi.range(dateapi.check_convert(from_date),
                           dateapi.check_convert(to_date))

    if raw_input("This script will overwrite db (~/.tips_db) if it exists. \
            Continue? (y/N)") in ('y', 'yes', 'Y', 'Yes', 'YES'):
        pass
    else:
        print "\ndoing nothing..."
        exit(1)

    db.data = {}

    for item in result:
        db.replace(item, float(randint(1, int(in_range))))

    db.save()

    print "\nDone."
