# -*- coding: utf-8 -*-

import logging
import optparse


class OptionParser(optparse.OptionParser, object):
    """
        Option Parser with default options for log level handling

        - log-level defines level for every loggers instanced when the object OptionParser is created
        - log-filter defines level for specific loggers identified by their names.
        - Example
        script.py --log-level info --log-filter lib1:debug,lib2:error
    """
    def __init__(self, *args, **kwargs):
        super(OptionParser, self).__init__(*args, **kwargs)
        self.add_option("", "--log-level", dest="log_level", default="info", help="verbosity : debug, info, warning, error, critical")
        self.add_option("", "--log-filter", dest="log_filter", default="", help="")

    def parse_args(self):
        options, args = super(OptionParser, self).parse_args()
        default_level = getattr(logging, options.log_level.upper())
        for l in logging.Logger.manager.loggerDict.values():
            if isinstance(l, logging.Logger):
                l.setLevel(default_level)
        if options.log_filter:
            for logger_name, level in [token.split(":") for token in options.log_filter.split(",")]:
                logging.getLogger(logger_name).setLevel(getattr(logging, level.upper()))
        return options, args
