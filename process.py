import sys
import re
import collections
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
        return ExpectDate()

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

    def register(self, changed, callback):
        if changed not in Context.valid_keys:
            raise ValueError('Cannot register for change in ' + changed)

        self.handlers[changed].append(callback)

    def handle(self, line):
        if line.strip():
            self.state = self.state.handle(self, line)
        return self.state

def date_changed(changed, old, new, ctx_data):
    print(changed, 'changed')
    print('\tfrom', old, 'to', new)

if __name__ == '__main__':
    fname = sys.argv[1]
    verbose = False
    if '-v' in sys.argv:
        verbose = True

    num_lines = 0

    ctx = Context()
    ctx.register(changed='date', callback=date_changed)
    with open(fname, 'r') as f:
        for line in f:
            num_lines += 1
            ctx.handle(line)

    if verbose:
        print('Processed', num_lines, 'lines')
