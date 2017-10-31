class Address(object):
    def __init__(self, segment, offset):
        self.segment = segment
        self.offset = offset

    def __str__(self):
        return '%04X:%04X' % (self.segment, self.offset)

    def __add__(self, other):
        if isinstance(other, int):
            return Address(self.segment, self.offset + other)
        else:
            raise Exception