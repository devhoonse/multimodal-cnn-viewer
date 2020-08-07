
from . import AbstractProcessor
from ..configs import ApplicationConfiguration

from multiprocessing import Lock


class Preprocessor(AbstractProcessor):
    def __init__(self):
        super(Preprocessor, self).__init__()

    def run(self, *args, **kwargs):
        print(self.__class__.run)  # for debugging
        super(Preprocessor, self).run(*args, **kwargs)
