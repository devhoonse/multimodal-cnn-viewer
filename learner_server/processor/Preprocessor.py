from ..common import SingletonInstance
from ..configs import ApplicationConfiguration


class Preprocessor(SingletonInstance):
    def __init__(self):
        pass

    def init(self, config: ApplicationConfiguration):
        pass

    def run(self, *args, **kwargs):
        while True:
            1 == 1
