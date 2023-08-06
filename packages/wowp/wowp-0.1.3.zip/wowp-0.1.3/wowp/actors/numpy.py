from . import Actor


class Rand(Actor):
    def __init__(self, name=None):
        super(Rand, self).__init__(name=name)
        self.inports.append('n')
        self.outports.append('out')

    def get_args(self):
        args = (self.inports['n'].pop(),)
        kwargs = {}
        return args, kwargs

    @staticmethod
    def get_result(*args, **kwargs):
        from numpy.random import rand
        return {'out': rand(*args)}

    def run(self):
        args, kwargs = self.get_args()
        return self.get_result(*args, **kwargs)


class RandInt(Actor):
    def __init__(self, name=None):
        super(RandInt, self).__init__(name=name)
        self.inports.append('low')
        self.outports.append('out')

    def get_args(self):
        args = (1, self.inports['low'].pop(),)
        kwargs = {}
        return args, kwargs

    @staticmethod
    def get_result(*args, **kwargs):
        from numpy.random import randint
        return {'out': randint(*args)}

    def run(self):
        args, kwargs = self.get_args()
        return self.get_result(*args, **kwargs)
