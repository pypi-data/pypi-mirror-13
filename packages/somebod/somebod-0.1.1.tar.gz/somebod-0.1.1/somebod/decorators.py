# -*- coding: utf-8 -*-

import hashlib
import logging
import os
import pickle
import time


def timed_task(logger, level=logging.INFO):
    """
        Print time elapsed for executing a function
    """
    def task(func):
        def wrapper(*args, **kwargs):
            start = time.time()
            retval = func(*args, **kwargs)
            time_elapsed = time.time() - start
            func_name = func.__name__
            msg = "Executed %(func_name)s in %(time_elapsed).2fs with args=%(args)s, kwargs=%(kwargs)s" % locals()
            logger.log(level, msg)
            return retval
        return wrapper
    return task


def cached_task(directory, logger):
    """
        Cache result of a function for specific arguments in a file.

        - Create a file based on the hash of function name and arguments serialized as string
        - Save output in a pickle format
        - Ignore corrupted files
        - Raise error if directory is not there
    """
    def task(func):
        def wrapper(*args, **kwargs):
            if not os.access(directory, os.W_OK):
                raise OSError("%(directory)s is not writable" % locals())
            hh = hashlib.md5(func.__name__ + str(*args) + str(*kwargs)).hexdigest()
            fn = os.path.join(directory, ".%(hh)s.pickle" % locals())
            if os.path.exists(fn) and os.path.isfile(fn):
                try:
                    retval = pickle.load(open(fn, "r"))
                    logger.debug("Loaded result from %(fn)s" % locals())
                    return retval
                except Exception as e:
                    logger.warning("Impossible to load from %(fn)s, %(e)s" % locals())
            retval = func(*args, **kwargs)
            if directory:
                try:
                    pickle.dump(retval, open(fn, "w+"))
                    logger.debug("Dumped result to %(fn)s" % locals())
                except Exception as e:
                    logger.error("Impossible to dump to %(fn)s, %(e)s" % locals())
            return retval
        return wrapper
    return task
