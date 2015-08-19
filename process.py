import sys
import re
import dateutil.parser

class ExpectStart(object):
    def handle(self, ctx, line):
        return self

class ExpectDate(object):
    def handle(self, ctx, line):
        date_str = line[len('## '):]
        date = dateutil.parser.parse(date_str)
        ctx.date = date
        return ExpectStart()

class ExpectWeek(object):
    week_re = re.compile('week ?(\d+)', re.IGNORECASE)

    def handle(self, ctx, line):
        ctx.week = ExpectWeek.week_re.search(line).group(1)
        return ExpectDate()

class Context(object):
    def __init__(self):
        self.state = ExpectWeek()
        self.week = None
        self.date = None

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

            print('Line {line_num}: "{line}"'.format(line_num=num_lines,
                line=line.strip()))
            print('\tWeek', ctx.week)
            print('\tDate', ctx.date)

    if verbose:
        print('Processed', num_lines, 'lines')
