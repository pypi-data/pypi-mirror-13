# -*- coding: utf-8 -*-

import os
import time


def os_query(qry, logger):
    """
        Human wrapper for os.system function

        - Raise OSError if something went wrong
        - Print time elapsed
    """
    start = time.time()
    retval = os.system(qry)
    duration = time.time() - start
    if retval:
        logger.error("[%(duration).2fs], retval=%(retval)s, %(qry)s" % locals())
        raise OSError("Cannot execute %(qry)s" % locals())
    else:
        logger.info("[%(duration).2fs], retval=%(retval)s, %(qry)s" % locals())


def remove_and_create_directory(directory):
    os_query("rm -rf %(directory)s" % locals())
    os_query("mkdir -p %(directory)s" % locals())


def create_directory(directory):
    os_query("mkdir -p %(directory)s" % locals())
