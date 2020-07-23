# -*- coding: utf-8 -*-

from ..common import SingletonInstance
from ..configs import ApplicationConfiguration
from ..manager import ProcessManager
from ..processor import *


class Learner(SingletonInstance):
    def __init__(self):
        self._parent = None         # type: ProcessManager
        self.loader = None          # type: Loader
        self.preprocessor = None    # type: Preprocessor
        self.evaluator = None       # type: Evaluator
        self.predictor = None       # type: Predictor

        self._STEP_MAP: dict = {
            'STEP01': self.loader.run,
            'STEP02': self.preprocessor.run,
            'STEP03': self.evaluator.run,
            'STEP04': self.predictor.run
        }

    def init(self, parent: ProcessManager, config: ApplicationConfiguration):
        self._parent = parent
        self.loader = Loader.instance()
        self.preprocessor = Preprocessor.instance()
        self.evaluator = Evaluator.instance()
        self.predictor = Predictor.instance()

        self.loader.init(config)
        self.preprocessor.init(config)
        self.evaluator.init(config)
        self.predictor.init(config)

    def get_target_job(self, step) -> callable:
        return self._STEP_MAP[step]

    def load_data(self, *args, **kwargs):
        pass

    def preprocess_data(self, *args, **kwargs):
        pass

    def fit_model(self, *args, **kwargs):
        pass

    def predict_data(self, *args, **kwargs):
        pass
