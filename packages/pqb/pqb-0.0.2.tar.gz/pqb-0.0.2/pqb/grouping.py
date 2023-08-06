class ConditionalGrouping(list):
    def __init__(self, *args, **kwargs):
        super(ConditionalGrouping, self).__init__(*args, **kwargs)
    def result(self):
        return ' '.join( list( map(lambda x: x.result(), self) ) )

class ANDConditionalGrouping(ConditionalGrouping):
    def __init__(self, *args, **kwargs):
        super(ANDConditionalGrouping, self).__init__(*args, **kwargs)
    def result(self):
        return ' AND '.join( list( map(lambda x: x.result(), self) ) )

class ORConditionalGrouping(ConditionalGrouping):
    def __init__(self, *args, **kwargs):
        super(ORConditionalGrouping, self).__init__(*args, **kwargs)
    def result(self):
        return ' OR '.join( list( map(lambda x: x.result(), self) ) )
