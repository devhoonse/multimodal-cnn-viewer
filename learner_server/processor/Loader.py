
from ..configs import ApplicationConfiguration
from . import AbstractProcessor

from multiprocessing import Lock


class Loader(AbstractProcessor):
    def __init__(self):
        super(Loader, self).__init__()

    def run(self, *args, **kwargs):
        print(self.__class__.run)  # for debugging
        super(Loader, self).run(*args, **kwargs)
