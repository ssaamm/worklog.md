import sys
import re
import dateutil.parser

class DoNothingState(object):
    def handle(self, ctx, line):
        return self

class ExpectStart(object):
    start_re = re.compile('start @ ([0-9:]+)', re.IGNORECASE)

    def handle(self, ctx, line):
        start_str = ExpectStart.start_re.search(line).group(1)
        ctx['start'] = dateutil.parser.parse(start_str)
        return DoNothingState()

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

    def __getitem__(self, key):
        return self.__dict[key]

    def __setitem__(self, key, value):
        if key not in Context.valid_keys:
            raise KeyError('Invalid key ' + key)
        print(key, '=', value)
        self.__dict[key] = value

    def handle(self, line):
        if not line.strip(): return
        self.state = self.state.handle(self, line)

if __name__ == '__main__':
    fname = sys.argv[1]
    verbose = False
    if '-v' in sys.argv:
        verbose = True

    num_lines = 0

    ctx = Context()
    with open(fname, 'r') as f:
        for line in f:
            num_lines += 1
            ctx.handle(line)

    if verbose:
        print('Processed', num_lines, 'lines')
