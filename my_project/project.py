"""Define the project's workflow logic."""
from math import ceil

from flow import FlowProject
from flow import JobOperation

import logging

logger = logging.getLogger(__name__)


class MyProject(FlowProject):

    def classify(self, job):
        "Classify this job by yielding 'labels' based on the job's status."
        num_steps = job.document.get('sample_step', 0)
        if job.isfile('init.gsd'):
            yield 'initialized'
        if 'volume_estimate' in job.document:
            yield 'estimated'
        if num_steps > 0:
            yield 'started'
        if num_steps >= 5000 and job.isfile('dump.log'):
            yield 'sampled'

    def next_operation(self, job):
        "Determine the next job, based on the job's data."
        labels = set(self.classify(job))

        def op(name):
            "Construct default job operation."
            return JobOperation(name, job, 'python scripts/run.py {} {}'.format(name, job))

        if 'initialized' not in labels:
            return op('initialize')
        if 'estimated' not in labels:
            return op('estimate')
        if 'sampled' not in labels:
            return op('sample')

    def submit_user(self, env, _id, operations, walltime, np, ppn,
                    serial=False, force=False, **kwargs):
        "Write commands for operations to job script."
        # Calculate the total number of required processors
        np_total = np if serial else np * len(operations)
        # Calculate the total number of required nodes
        nn = ceil(np_total / ppn)

        if not force:  # Perform basic check concerning the node utilization.
            usage = np * len(operations) / nn / ppn
            if usage < 0.9:
                raise RuntimeError("Bad node utilization!")

        # Create a submission script.
        sscript = env.script(_id=_id, walltime=walltime, nn=nn, ppn=ppn,
                             serial=serial, **kwargs)

        # Add some whitespace
        sscript.writeline()
        # Don't use uninitialized environment variables.
        sscript.writeline('set -u')
        # Exit on errors.
        sscript.writeline('set -e')
        # Writing HOOMD_WALLTIME_STOP
        # Does not hurt even if we don't use HOOMD-blue.
        walltime_seconds = 24 * 3600 * walltime.days + walltime.seconds
        sscript.writeline(
            'export HOOMD_WALLTIME_STOP=$((`date +%s` + {}))'.format(
                int(0.9 * walltime_seconds)))
        # Switch into the project root directory
        sscript.writeline('cd {}'.format(self.root_directory()))
        sscript.writeline()

        # Iterate over all job-operations and write the command to the script
        for op in operations:
            self.write_human_readable_statepoint(sscript, op.job)
            sscript.write_cmd(op.cmd, np=np, bg=not serial)

        # Wait until all processes have finished
        sscript.writeline('wait')

        # Submit the script to the environment specific scheduler
        return env.submit(sscript, **kwargs)


def get_project(*args, **kwargs):
    """Find a project configuration and return the associated project.

    This is a wrapper for: :py:meth:`.MyProject.get_project`
    """
    return MyProject.get_project(*args, **kwargs)
