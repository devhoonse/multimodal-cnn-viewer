
from . import AbstractProcessor
from ..configs import ApplicationConfiguration

from multiprocessing import Lock


class Evaluator(AbstractProcessor):
    def __init__(self):
        super(Evaluator, self).__init__()

    def run(self, *args, **kwargs):
        while True:
            1 == 1
