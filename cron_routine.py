# -*- coding: utf-8 -*-

# 매 분마다 실행하기
# [prompt]# crontab -e
# * * * * * /path/to/python -u ~/cnn/executor/cron_routine.py

from learner_server.configs import ApplicationConfiguration
from learner_server.utils import LogHandler
from learner_server.dao import OracleDataSource, AbstractSession
from learner_server.manager import ProcessManager


def cron_routine():
    """
    Defines the Activity Sequence of Cron-Job every 1 Minutes
    """

    config: ApplicationConfiguration = ApplicationConfiguration.instance()
    config.init('config.properties')

    log_handler: LogHandler = LogHandler.instance()
    log_handler.init(config)
    logger = log_handler.get_logger()

    data_source: OracleDataSource = OracleDataSource.instance()     # Todo: Make Available Various Types of Data Sources
    data_source.init(config)
    session: AbstractSession = data_source.get_session()

    process_manager = ProcessManager.instance()
    process_manager.init(config)

    # 1. Assign Jobs from Queue to Process
    process_manager.assign_jobs_from_queue(session)

    # 2. Stop Process(es) which are Requested from Web UI
    canceled_processes: list = process_manager.cancel_processes(session)

    # 3. Start Process(es) which are not in processing
    started_processes: list = process_manager.run_newly_assigned_processes(session)

    # for Debugging
    current_processes: list = process_manager.search_current_processes(session)

    # X. Close the Database Session
    session.close()
    OracleDataSource.instance().close()


if __name__ == '__main__':

    cron_routine()
