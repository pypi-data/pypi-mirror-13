class TooManyNoMessageError(Exception):

    """Docstring for ToManyNoMessageError. """

    def __init__(self, value):
       self.value = value

    def __str__(self):
        return repr(self.value)

