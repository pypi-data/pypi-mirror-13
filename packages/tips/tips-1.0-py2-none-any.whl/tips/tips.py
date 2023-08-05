#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""tips.py - A tips per day tracker and displayer
for malnourished underpaid service industry workers."""

from sys import argv
import argparse
from . import db
from . import dateapi
from . import minigraph
from . import stats

### argparse setup ###

HELP_TEXT = """
A tips per day tracker and displayer for malnourished underpaid service industry workers.
"""

EPILOG_TEXT = """
example usage:
  add 20                add 20 to today's value
  reduce 15             reduce today's value by 15
  add 12 1d             add 12 to yesterday's value
  set 30 1w             replace the value for the date of 1 week ago with 30
  show 2015-12-1        show the value for said date
  show 0d 30d           list all the records from the past 30 days
  graph 30d 0d          print a graph of the past 30 days
"""

def parse_args(in_args):
    """
    Setup argparse, parse args, and return dict.
    """
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                                     description=HELP_TEXT, epilog=EPILOG_TEXT)

    subparsers = parser.add_subparsers(dest='cmd')

    add_command = subparsers.add_parser('add', help="increase value under date by amount")
    add_command.add_argument('amount', help="amount to add")
    add_command.add_argument('date', default='today', nargs='?',
                             help="""date to affect (default today)
                             specified in the format YYYY-MM-DD
                             OR by how much time ago e.g. 9d2w or 1d or 4y23d.""")

    reduce_command = subparsers.add_parser('reduce', help="decrease value under date by amount")
    reduce_command.add_argument('amount', help="amount to add")
    reduce_command.add_argument('date', default='today', nargs='?',
                                help="""date to affect (default today)
                                specified in the format YYYY-MM-DD
                                OR by how much time ago e.g. 9d2w or 1d or 4y23d.""")

    set_command = subparsers.add_parser('set', help="replace value under date with amount")
    set_command.add_argument('amount', help="amount to add")
    set_command.add_argument('date', default='today', nargs='?',
                             help="""date to affect (default today)
                             specified in the format YYYY-MM-DD
                             OR by how much time ago e.g. 9d2w or 1d or 4y23d.""")

    show_command = subparsers.add_parser('show',
                                         help="show value(s) under date or range of dates")
    show_command.add_argument('date', default='today',
                              help="""date to show
                              specified in the format YYYY-MM-DD
                              OR by how much time ago e.g. 9d2w or 1d or 4y23d.""")
    show_command.add_argument('to', default=None, nargs='?',
                              help="""to date (default none)
                              specified in the format YYYY-MM-DD
                              OR by how much time ago e.g. 9d2w or 1d or 4y23d.""")

    graph_command = subparsers.add_parser('graph', help="graph of values in date range")
    graph_command.add_argument('from',
                               help="""from date
                               specified in the format YYYY-MM-DD
                               OR by how much time ago e.g. 9d2w or 1d or 4y23d.""")
    graph_command.add_argument('to',
                               help="""to date
                               specified in the format YYYY-MM-DD
                               OR by how much time ago e.g. 9d2w or 1d or 4y23d.""")

    stats_command = subparsers.add_parser('stats', help="show assorted stats")
    ## Hidden testing command
    stats_command.add_argument('--test-gen-db', action='store_true', dest='test_gen',
                               help=argparse.SUPPRESS)

    args = vars(parser.parse_args(in_args))

    ### extra logic ###

    try:
        if args['date'] == 'today':
            args['date'] = dateapi.today()
        else:
            args['date'] = dateapi.check_convert(args['date'])

        if args['date'] is False:
            print "Invalid date(s)."
            exit(1)
    except KeyError:
        pass

    try:
        if args['from'] == 'today':
            args['from'] = dateapi.today()
        else:
            args['from'] = dateapi.check_convert(args['from'])

        if args['from'] is False:
            print "Invalid date(s)."
            exit(1)
    except KeyError:
        pass

    try:
        if args['to'] == 'today':
            args['to'] = dateapi.today()
        elif args['to'] is None:
            pass
        else:
            args['to'] = dateapi.check_convert(args['to'])

        if args['to'] is False:
            print "Invalid date(s)."
            exit(1)
    except KeyError:
        pass

    try:
        args['amount'] = float(args['amount'])
    except ValueError:
        print "Invalid amount."
        exit(1)
    except KeyError:
        pass

    try:
        if args['test_gen']:
            from . import test_gen_db
            test_gen_db.generate('1y', '0d', '30')
            exit(0)
    except KeyError:
        pass

    return args



def table(dates, amounts, spacing=-16):
    """Print table."""
    amounts = [int(i) if i == int(i) else i for i in amounts] # See note 1 (bottom)

    amounts_max_len = max([len(str(x)) for x in amounts])

    print "-" * ((spacing*-1) + amounts_max_len)

    for date, amount in zip(dates, amounts):
        print "%*s%s" % (spacing, date, amount)

    print "-" * ((spacing*-1) + amounts_max_len)

def add_action(args):
    result = db.add(args['date'], args['amount'])

    if result is False:
        print "Invalid amount."
        exit(1)
    else:
        show_action(args)

def reduce_action(args):
    result = db.reduce(args['date'], args['amount'])

    if result is False:
        print "Invalid amount."
        exit(1)
    elif result is None:
        print "Record removed."
    else:
        show_action(args)

def set_action(args):
    result = db.replace(args['date'], args['amount'])

    if result is False:
        print "Invalid amount."
        exit(1)
    elif result is True:
        show_action(args)
    else:
        print "Record removed."

def show_action(args):
    try:
        results = db.get_range(args['date'], args['to'])
        results = zip(*results)

        if results is None:
            print "No entries."
        else:
            table(results[0], results[1])
    except (KeyError, AttributeError, TypeError):
        result = db.get_item(args['date'])

        if result is None:
            print "No record."
        else:
            table([result[0]], [result[1]])

def graph_action(args):
    results = db.get_range(args['from'], args['to'])

    if results is None:
        print "No entries."
    else:
        results = [b for a, b in results]
        print_graph = minigraph.auto(results)
        for i in print_graph:
            print i


def main():
    ## Convert Namespace object into usable dict.
    ## We can call our functions with a simple 'funcs[command](args)'
    args = parse_args(argv[1:])
    command = args.pop('cmd')


    # go
    funcs = {
        'add': add_action,
        'reduce': reduce_action,
        'set': set_action,
        'show': show_action,
        'graph': graph_action,
        'stats': stats.print_stats
    }

    if command == 'stats':
        funcs[command]()
    else:
        funcs[command](args)

    db.save()

### Footnotes ###

## 1. This is a nice example of a one-liner changing the result drastically.
##    Turns any real number which is a float e.g. 1.0, into an int e.g. 1
##    Because the line is in a function used for every action,
##    the whole program is affected.
