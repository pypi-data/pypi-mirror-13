Adapted logger
==============

A helper log library based on default logging module permetting a custom
format of logs to be redirected to Logstash - Elasticsearch - Kibana.

----

*************
Custom usage:
*************

HOW TO INSTALL

* Install adapted_logger using easy_setup or pip::

   pip install adapted_logger

HOW TO USE::

 from logger.adapted_logger import AdaptedLogger
 logger = AdaptedLogger("project_name", "127.0.0.1") # specify project_name and ip address of current server
 log = logger.get_logger()
 log.info("This is an info message")
 log.debug("This is a debug message")
 log.warn("This is a warning message")
 log.error("This is an error message")

RESULTS::

 2015-10-27 17:06:50,176 project_name INFO 127.0.0.1 This is an info message
 2015-10-27 17:06:55,552 project_name DEBUG 127.0.0.1 This is a debug message
 2015-10-27 17:07:00,863 project_name WARNING 127.0.0.1 This is a warning message
 2015-10-27 17:07:05,360 project_name ERROR 127.0.0.1 This is an error message

*************************
Redirect logs to console:
*************************

Instantiate AdaptedLogger object::

 adapted_log = AdaptedLogger("retail_crm_server", "127.0.0.1")

Redirect logs to console (Default behavior)::

 adapted_log.redirect_to_console()

Get logger object::

 logger = adapted_log.get_logger()
 logger.debug("Testing Debug Message")
 logger.info("Testing Info Message")
 logger.warn("Testing Warn Message")
 logger.error("Testing Error Message")

**********************
Redirect logs to file:
**********************

Instantiate AdaptedLogger object::

 adapted_log = AdaptedLogger("retail_crm_server", "127.0.0.1")

Redirect logs to file::

 adapted_log.redirect_to_file("/path/logfile.log")

Get logger object::

 logger = adapted_log.get_logger()
 logger.debug("Testing Debug Message")
 logger.info("Testing Info Message")
 logger.warn("Testing Warn Message")
 logger.error("Testing Error Message")


**************
Custom adapter
**************
This adds the possibility to configure your logger within a config file like config.yml,
inside /config folder you should specify your configuration in YAML format.

formatters::

        simpleFormater:
            format: '%(asctime)s    %(name)s    %(levelname)s    %(message)s'
            datefmt: '%Y/%m/%d %H:%M:%S's

Here we specify time, package name, level name, and the message, right now there is no injection of the ip address

handlers ::

    console:
        class: logging.StreamHandler
        formatter: simpleFormater
        level: DEBUG
        stream: ext://sys.stdout
    file:
        class : logging.FileHandler
        formatter: simpleFormater
        level: WARNING
        filename: filename_or_path.log

Here we specify handlers, in this exemple we use 2 handlers : console and file.

loggers::

    clogger:
        level: DEBUG
        handlers: [console]
    flogger:
        level: WARNING
        handlers: [file]

And finally we create 2 loggers for console and file handlers.

To inject ip address into context, we have created CustomAdapter class that create an adapter and inject ip in the
process.

Usage ::

    logging_config = yaml.load(open('config/config.yml', 'r'))
    dictConfig(logging_config)

    logger_1 = logging.getLogger("project_name.application_name1")
    logger_1 = CustomAdapter(logger_1, {'ip': ip})

    logger_2 = logging.getLogger("project_name.application_name2")
    logger_2 = CustomAdapter(logger_2, {'ip': ip})

Right now, we can call ::

    logger_1.warning('This is a warning Message')
    logger_2.error('This is an error message)
