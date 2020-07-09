import logging
import logging.config
import json

from ..common import SingletonInstance
from .. import ApplicationConfiguration


class LogHandler(SingletonInstance):
    """
    logging.Logger를 관리하는 Handler 클래스
    """

    def __init__(self):
        # logging.Logger 인스턴스
        self._logger: logging.Logger = None  # Logger 인스턴스 할당을 위한 변수 선언

    def init(self, config: ApplicationConfiguration):
        """
            Logger Configuration, Logger 설정파일인 ./resources/m4_log.json 파일을 읽어들여서 설정함
        :param config: Application Configuration
        :return: void
        """

        with open(config.find("Server", "log.file"), "rt") as f:
            config = json.load(f)

        logging.config.dictConfig(config)
        self._logger = logging.getLogger()

    def get_logger(self) -> logging.Logger:
        return self._logger