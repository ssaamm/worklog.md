'''
Usage examples:

Process the file worklog.md:

    python process.py worklog.md

(By default, output figure is saved in whatever your filename is appended with
'.png', so 'worklog.md.png' in this case)

Process the file worklog.md, storing output in foo.png:

    python process.py worklog.md foo.png
'''
import sys
import re
import collections
import functools
import dateutil.parser

import matplotlib.mlab as mlab
import matplotlib.pyplot as plt
import numpy as np

class ExpectDescription(object):
    def handle(self, ctx, line):
        if line.find('# ') == 0:
            ctx.state = ExpectWeek()
            return ctx.handle(line)
        if line.find('## ') == 0:
            ctx.state = ExpectDate()
            return ctx.handle(line)
        return self

class ExpectEnd(object):
    end_re = re.compile('stop @ ([0-9:]+)', re.IGNORECASE)

    def handle(self, ctx, line):
        end_str = ExpectEnd.end_re.search(line).group(1)
        ctx['end'] = dateutil.parser.parse(end_str)
        return ExpectDescription()

class ExpectLunch(object):
    lunch_re = re.compile('lunch:? ([0-9:]+)-([0-9:]+)', re.IGNORECASE)

    def handle(self, ctx, line):
        match = ExpectLunch.lunch_re.search(line)
        if match:
            ctx['lunch_start'] = dateutil.parser.parse(match.group(1))
            ctx['lunch_end'] = dateutil.parser.parse(match.group(2))
        else:
            ctx['lunch_start'] = None
            ctx['lunch_end'] = None
        return ExpectEnd()

class ExpectStart(object):
    start_re = re.compile('start @ ([0-9:]+)', re.IGNORECASE)

    def handle(self, ctx, line):
        start_str = ExpectStart.start_re.search(line).group(1)
        ctx['start'] = dateutil.parser.parse(start_str)
        return ExpectLunch()

class ExpectDate(object):
    def handle(self, ctx, line):
        date_str = line[len('## '):]
        date = dateutil.parser.parse(date_str)
        ctx['date'] = date
        return ExpectStart()

class ExpectWeek(object):
    week_re = re.compile('week ?(\d+)', re.IGNORECASE)

    def handle(self, ctx, line):
        ctx['week'] = ExpectWeek.week_re.search(line).group(1)
        return ExpectDescription()

class Context(object):
    valid_keys = {'week', 'date', 'start', 'end', 'lunch_start', 'lunch_end'}

    def __init__(self):
        self.state = ExpectWeek()
        self.__dict = {}
        self.handlers = collections.defaultdict(list)

    def __getitem__(self, key):
        try:
            return self.__dict[key]
        except KeyError:
            if key in Context.valid_keys:
                return None
            raise

    def __contains__(self, item):
        return item in self.__dict

    def __setitem__(self, key, value):
        if key not in Context.valid_keys:
            raise KeyError('Invalid key ' + key)

        for handler in self.handlers[key]:
            handler(changed=key, old=self[key], new=value, ctx_data=dict(self.__dict))

        self.__dict[key] = value

    def register(self, changed, handler):
        if changed not in Context.valid_keys:
            raise ValueError('Cannot register for change in ' + changed)

        self.handlers[changed].append(handler)

    def handle(self, line):
        if line.strip():
            self.state = self.state.handle(self, line)
        return self.state

def save_stats(changed, old, new, ctx_data, stats):
    if not old: return
    stats[old] = ctx_data

def hours_diff(end, start):
    if not end or not start:
        return 0
    diff = end - start
    return diff.total_seconds() / 3600

if __name__ == '__main__':
    fname = sys.argv[1]
    output = sys.argv[2] if len(sys.argv) > 2 else sys.argv[1] + '.png'

    day_to_stats = {}
    save_day_stats = functools.partial(save_stats, stats=day_to_stats)

    ctx = Context()
    ctx.register(changed='date', handler=save_day_stats)

    with open(fname, 'r') as f:
        for num, line in enumerate(f):
            try:
                ctx.handle(line)
            except:
                print('Error on line', num + 1, '-', line.strip())
                exit()

    time_at_lunch = [hours_diff(s['lunch_end'], s['lunch_start']) for d, s in day_to_stats.items()]
    time_at_office = [hours_diff(s['end'], s['start']) for d, s in day_to_stats.items()]
    time_working = [t[0] - t[1] for t in zip(time_at_office, time_at_lunch)]

    fig, axes = plt.subplots(ncols=2, figsize=(6,6))
    axes[0].boxplot(time_at_lunch)
    axes[1].boxplot([time_working, time_at_office])
    plt.savefig(output)
