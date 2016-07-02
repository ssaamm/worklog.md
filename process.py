'''
Usage examples:

Process the file worklog.md:

    python process.py worklog.md

(By default, output figure is saved in whatever your filename is appended with
'.png', so 'worklog.md.png' in this case)

Process the file worklog.md, storing output in foo.png:

    python process.py worklog.md foo.png
'''
from antlr4 import FileStream, CommonTokenStream, ParseTreeWalker
from day_stats_walker import DayStatsWalker
from itertools import groupby
from parsing import WorklogLexer, WorklogParser
import sys

def sorted_groupby(iterable, key=None):
    return groupby(sorted(iterable, key=key), key=key)

def hours_diff(end, start):
    if not end or not start:
        return 0
    diff = end - start
    return diff.total_seconds() / 3600

def print_hours_per_week(day_to_stats):
    def year_week(day_to_stat):
        ic = day_to_stat[0].isocalendar()
        return ic[0], ic[1]

    for week, day_stats in sorted_groupby(day_to_stats.items(), key=year_week):
        day_stats = list(day_stats)

        time_at_lunch = [0 if s['is_lunch_business'] else hours_diff(s['lunch_end'], s['lunch_start']) for d, s in day_stats]
        time_at_office = [hours_diff(s['end'], s['start']) + hours_diff(s['extra_end'], s['extra_start'])for d, s in day_stats]
        time_working = [t[0] - t[1] for t in zip(time_at_office, time_at_lunch)]

        print('{}w{} - {:.02f}h'.format(week[0], week[1], sum(time_working)))

def print_hours_per_day(day_to_stats):
    for day, stats in sorted(day_to_stats.items()):
        time_at_lunch = hours_diff(stats['lunch_end'], stats['lunch_start'])
        if stats['is_lunch_business']:
            time_at_lunch = 0
        time_at_office = hours_diff(stats['end'], stats['start']) + hours_diff(stats['extra_end'], stats['extra_start'])

        print(day.strftime('%Y-%m-%d:'), time_at_office - time_at_lunch)

if __name__ == '__main__':
    daily = True
    try:
        option = sys.argv[2]
        if option == '-w':
            daily = False
    except IndexError:
        pass

    input_file = FileStream(sys.argv[1])
    lexer = WorklogLexer(input_file)
    stream = CommonTokenStream(lexer)
    parser = WorklogParser(stream)
    tree = parser.wl()

    stats_walker = DayStatsWalker()
    walker = ParseTreeWalker()
    walker.walk(stats_walker, tree)
    stats_walker._save_current_stats()

    day_to_stats = stats_walker.stats

    if daily:
        print_hours_per_day(day_to_stats)
    else:
        print_hours_per_week(day_to_stats)
