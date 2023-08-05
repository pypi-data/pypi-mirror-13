__author__ = 'Sinisa'


class SBGError(Exception):

    def __init__(self, msg):
        self.message = msg

    def __str__(self):
        return self.message


class InvalidName(SBGError):
    pass
