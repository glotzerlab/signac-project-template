import os
import logging
from datetime import datetime
from contextlib import contextmanager

from signac.common import six

from .misc import cast_json

logger = logging.getLogger(__name__)


def redirect_log_file(job):
    import hoomd
    cleanup_log_file(job)
    fn_log = job.fn('hoomd_{}.log'.format(hoomd.comm.get_partition()))
    fn_log_tmp = fn_log + '.tmp'
    if hoomd.comm.get_rank() == 0:
        if os.path.isfile(fn_log):
            try:
                with open(fn_log, 'rb') as logfile:
                    with open(fn_log_tmp, 'ab') as tmplogfile:
                        tmplogfile.write(logfile.read())
            except IOError as error:
                logger.debug(error)
        hoomd.option.set_msg_file(fn_log)


def cleanup_log_file(job):
    import hoomd
    fn_log = job.fn('hoomd_{}.log'.format(hoomd.comm.get_partition()))
    fn_log_tmp = fn_log + '.tmp'
    if hoomd.comm.get_rank() == 0:
        try:
            with open(fn_log, 'rb') as logfile:
                with open(fn_log_tmp, 'ab') as tmplogfile:
                    tmplogfile.write(logfile.read())
                    tmplogfile.flush()
            if six.PY2:
                os.rename(fn_log_tmp, fn_log)
            else:
                os.replace(fn_log_tmp, fn_log)
        except IOError as error:
            logger.debug(error)
        hoomd.option.set_msg_file(None)


def store_meta_data(job):
    import hoomd
    if not hoomd.init.is_initialized():
        return
    metadata = job.document.get('hoomd_meta', dict())
    metadata[str(datetime.now().timestamp())] = cast_json(hoomd.meta.dump_metadata())
    job.document['hoomd_meta'] = metadata


@contextmanager
def redirect_log(job):
    redirect_log_file(job)
    yield
    cleanup_log_file(job)
