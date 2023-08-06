class AlreadyStarted(Exception):

    def __init__(self, machine):
        self.error = "Machine %s is already running" % machine

    def __str__(self):
        return repr(self.error)
