
from ..configs import ApplicationConfiguration
from . import AbstractProcessor

from multiprocessing import Lock


class Loader(AbstractProcessor):
    def __init__(self):
        super(Loader, self).__init__()

    def run(self, *args, **kwargs):
        while True:
            1 == 1
