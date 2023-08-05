class Bunch:
    def __init__(self, **kwds):
        self.__dict__.update(kwds)

    def __repr__(self):
        """ Invertible* string-form of a Bunch.

            >>> b = Bunch(foo=Bunch(lol=True), hello=42, ponies='are pretty!')
            >>> print repr(b)
            Bunch(foo=Bunch(lol=True), hello=42, ponies='are pretty!')
            >>> eval(repr(b))
            Bunch(foo=Bunch(lol=True), hello=42, ponies='are pretty!')

            (*) Invertible so long as collection contents are each repr-invertible.
        """
        keys = self.__dict__.keys()
        keys.sort()
        args = ', '.join(['%s=%r' % (key, self.__dict__[key]) for key in keys])
        return '%s(%s)' % (self.__class__.__name__, args)

    def is_empty(self):
        return self.__dict__ == {}