# -*- coding: utf-8 -*-


# from . import *
from learner_server.configs import ApplicationConfiguration
from learner_server.utils import LogHandler
from learner_server.dao import OracleDataSource, AbstractSession
from learner_server.manager import ProcessManager


def cronjob():
    """
    Defines the Activity Sequence of Cron-Job
    """

    config: ApplicationConfiguration = ApplicationConfiguration.instance()
    config.init('./configs/config.properties')

    log_handler: LogHandler = LogHandler.instance()
    log_handler.init(config)
    logger = log_handler.get_logger()

    data_source: OracleDataSource = OracleDataSource.instance()
    data_source.init(config)
    session: AbstractSession = data_source.get_session()

    # 1. Query Process List
    ProcessManager.get_process_list(session)

    # 2. Assign New Process from Queue If Available

    # 3.


if __name__ == '__main__':

    cronjob()
