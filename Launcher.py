from learner_server.common import SingletonInstance
from learner_server.processor import *
from learner_server import ApplicationConfiguration


class Launcher(SingletonInstance):
    def __init__(self):
        self.loader = None
        self.preprocessor = None
        self.evaluator = None
        self.predictor = None

    def init(self, config: ApplicationConfiguration):
        self.loader = Loader.instance()
        self.preprocessor = Preprocessor.instance()
        self.evaluator = Evaluator.instance()
        self.predictor = Predictor.instance()

        self.loader.init(config)
        self.preprocessor.init(config)
        self.evaluator.init(config)
        self.predictor.init(config)
