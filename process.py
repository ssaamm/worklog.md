import sys
import re
import collections
import functools
import dateutil.parser

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
            ctx['lunch_start'] = match.group(1)
            ctx['lunch_end'] = match.group(2)
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

if __name__ == '__main__':
    fname = sys.argv[1]
    verbose = False
    if '-v' in sys.argv:
        verbose = True

    num_lines = 0

    ctx = Context()

    day_to_stats = {}
    save_day_stats = functools.partial(save_stats, stats=day_to_stats)

    ctx.register(changed='date', handler=save_day_stats)

    with open(fname, 'r') as f:
        for line in f:
            num_lines += 1
            try:
                ctx.handle(line)
            except:
                print('Error on line', num_lines, '-', line.strip())
                exit()

    if verbose:
        print('Processed', num_lines, 'lines')

    for day, stats in day_to_stats.items():
        print(day)
        print('\tIn office: ', stats['end'] - stats['start'])
