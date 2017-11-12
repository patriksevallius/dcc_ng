import io

class Overlay(object):
    def __init__(self, filename):
        self.overlay = io.open(filename, 'rb')

