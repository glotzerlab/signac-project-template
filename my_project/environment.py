"""Configuration of the project enviroment.

The environments defined in this module can be auto-detected.
This helps to define environment specific behaviour in heterogenous
environments.
"""
import logging

import flow
from flow.environment import get_environment
from flow.environment import format_timedelta


__all__ = ['get_environment']

logger = logging.getLogger(__name__)


class MyTorqueEnvironment(flow.environment.TorqueEnvironment):
    hostname_pattern = 'mymoabcluster.university.edu'
    cores_per_node = 16

    @classmethod
    def mpi_cmd(cls, cmd, np):
        return 'mpirun -np {np} {cmd}'.format(n=np, cmd=cmd)

    @classmethod
    def script(cls, _id, nn, walltime, ppn=None, **kwargs):
        if ppn is None:
            ppn = cls.core_per_node
        js = super(MyTorqueEnvironment, cls).script()
        js.writeline('#!/bin/sh -l')
        js.writeline('#PBS -j oe')
        js.writeline('#PBS -l nodes={}:ppn={}'.format(nn, ppn))
        js.writeline('#PBS -l walltime={}'.format(format_timedelta(walltime)))
        js.writeline('#PBS -q low')
        js.writeline('#PBS -N {}'.format(_id))
        js.writeline('#PBS -V')
        return js
