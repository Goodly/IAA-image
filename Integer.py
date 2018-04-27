class Integer(object) :
    def __init__(self, val=0) :
        self._val = int(val)
    def __add__(self, val) :
        if type(val) == Integer :
            return Integer(self._val + val._val)
        return self._val + val
    def __sub__(self, val):
        return self + Integer(-val._val)
    def __mul__(self, val):
        if type(val) == Integer :
            return Integer(self._val * val._val)
        return self._val * val
    def __truediv__(self, val):
        if type(val) == Integer :
            return Integer(self._val / val._val)
        return self._val / val
    def __floordiv__(self, val):
        if type(val) == Integer :
            return Integer(self._val // val._val)
        return self._val // val
    def __iadd__(self, val) :
        self._val += val
        return self
    def __str__(self) :
        return str(self._val)
    def __repr__(self) :
        return 'Integer(%s)' %self._val
    def __eq__(self, other):
        return self._val == other._val
