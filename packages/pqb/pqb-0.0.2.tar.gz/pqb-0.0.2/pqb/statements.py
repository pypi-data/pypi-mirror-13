class LimitStatement(object):
    def __init__(self, n):
        super(LimitStatement, self).__init__()
        self.n = n
    def result(self):
        return "LIMIT %s" % (self.n)

class SkipStatement(object):
    def __init__(self, n):
        super(SkipStatement, self).__init__()
        self.n = n
    def result(self):
        return "SKIP %s" % (self.n)

class FetchPlanStatement(object):
    def __init__(self, direction='*', depth=-1):
        super(FetchPlanStatement, self).__init__()
        self.direction = direction
        self.depth = depth

    def result(self):
        return "FETCHPLAN %s:%d" % (self.direction, self.depth)
