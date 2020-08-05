
from . import AbstractProcessor
from ..configs import ApplicationConfiguration

from multiprocessing import Lock


class Preprocessor(AbstractProcessor):
    def __init__(self):
        super(Preprocessor, self).__init__()

    def run(self, *args, **kwargs):
        while True:
            1 == 1
