# -*- coding: utf-8 -*-

from ..common import SingletonInstance
from ..configs import ApplicationConfiguration
from ..manager import ProcessManager
from ..processor import *


class Learner(SingletonInstance):
    """
    Maybe.. it would be deprecated...
    """

    def __init__(self):
        self._parent = None         # type: ProcessManager
        self.loader = None          # type: Loader
        self.preprocessor = None    # type: Preprocessor
        self.evaluator = None       # type: Evaluator
        self.predictor = None       # type: Predictor

        self._STEP_MAP: dict = {}

    def init(self, parent: ProcessManager = None):
        self._parent = parent
        self.loader = Loader.instance()
        self.preprocessor = Preprocessor.instance()
        self.evaluator = Evaluator.instance()
        self.predictor = Predictor.instance()

        self._STEP_MAP: dict = {
            'S01': self.loader.run,
            'S02': self.preprocessor.run,
            'S03': self.evaluator.run,
            'S04': self.predictor.run
        }

    def get_target_job(self, step) -> callable:
        return self._STEP_MAP[step]
