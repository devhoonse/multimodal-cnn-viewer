# -*- coding: utf-8 -*-


from learner_server.configs import ApplicationConfiguration
from learner_server.utils import LogHandler
from learner_server.dao import OracleDataSource
from learner_server import WebApplication


def main():

    config: ApplicationConfiguration = ApplicationConfiguration.instance()
    config.init('./configs/config.properties')

    log_handler: LogHandler = LogHandler.instance()
    log_handler.init(config)
    logger = log_handler.get_logger()

    data_source: OracleDataSource = OracleDataSource.instance()
    data_source.init(config)
    config.init_code(data_source)

    web_app: WebApplication = WebApplication.instance()
    web_app.init(config)
    web_app.launch()

    # try:
    #
    #     data_source: OracleDataSource = OracleDataSource.instance()
    #     data_source.init(config)
    #     config.init_code(data_source)
    #
    #     web_app: WebApplication = WebApplication.instance()
    #     web_app.init(config)
    #     web_app.launch()
    #
    # except Exception as e:
    #     pass


if __name__ == '__main__':
    main()
