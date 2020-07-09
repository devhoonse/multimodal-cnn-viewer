from . import ApplicationConfiguration, WebApplication
from .utils import LogHandler


def main():

    config: ApplicationConfiguration = ApplicationConfiguration.instance()
    config.init('config/config.properties')

    log_handler: LogHandler = LogHandler.instance()
    log_handler.init(config)

    web_app: WebApplication = WebApplication.instance()
    web_app.init(
        static_url='/home/istream3',
        host='0.0.0.0',
        port=8457
    )
    web_app.launch()


if __name__ == '__main__':
    main()
