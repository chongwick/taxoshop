import _csv


class BadIterator:
    def __init__(self):
        self.reader = None
        self.n = 0

    def __iter__(self):
        return self

    def __next__(self):
        self.n += 1
        if self.n == 1:
            try:
                next(self.reader)
            except StopIteration:
                pass
            return "a,b"
        if self.n == 2:
            return "x"
        raise StopIteration


iterator = BadIterator()
reader = _csv.reader(iterator)
iterator.reader = reader
next(reader)
