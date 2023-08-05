tips

usage: tips [-h] {add,reduce,set,show,graph,stats} ...

A tips per day tracker and displayer for malnourished underpaid service industry workers.

positional arguments:
  {add,reduce,set,show,graph,stats}
    add                 increase value under date by amount
    reduce              decrease value under date by amount
    set                 replace value under date with amount
    show                show value(s) under date or range of dates
    graph               graph of values in date range
    stats               show assorted stats

optional arguments:
  -h, --help            show this help message and exit

example usage:
  add 20                add 20 to today's value
  reduce 15             reduce today's value by 15
  add 12 1d             add 12 to yesterday's value
  set 30 1w             replace the value for the date of 1 week ago with 30
  show 2015-12-1        show the value for said date
  show 0d 30d           list all the records from the past 30 days
  graph 30d 0d          print a graph of the past 30 days



