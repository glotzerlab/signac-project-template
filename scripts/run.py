#!/usr/bin/env python
"""Execute job-operations.

By default this module will attempt to call functions
defined within the :py:mod:`.operations` module.
"""
import sys
import logging
import argparse

import signac

import operations


def main(args):
    # Get the project handle
    project = signac.get_project()

    # Default to all jobs if the jobid argument was ommitted.
    if not len(args.jobid):
        args.jobid = [job.get_id() for job in project.find_jobs()]

    logger = logging.getLogger()
    formatter = logging.Formatter(
        '%(asctime)s %(name)-12s %(levelname)-8s %(message)s')

    # Iterate through all ids and run the specifed job.
    for jobid in args.jobid:
        job = project.open_job(id=jobid)
        try:
            # The operation is assumed to be defined in the operations module.
            operation = getattr(operations, args.operation)
        except AttributeError:
            raise KeyError("Unknown operation '{}'.".format(args.operation))
        else:
            # Log output of this job.
            filehandler = logging.FileHandler(filename=job.fn('run.log'))
            filehandler.setFormatter(formatter)
            logger.addHandler(filehandler)
            try:
                operation(job)
            finally:
                logger.removeHandler(filehandler)
    return 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'operation',
        type=str,
        help="The operation to execute.")
    parser.add_argument(
        'jobid',
        type=str,
        nargs='*',
        help="The job ids, as registered in the signac project. "
             "Omit to default to all statepoints.")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO)
    sys.exit(main(args))
