"""This module contains the operation functions for this project.

Functions defined in this module can be executed using the
:py:mod:`.run` module.
"""
import logging
from math import ceil

from util.hoomd import redirect_log, store_meta_data


logger = logging.getLogger(__name__)
STEPS = 5000


def initialize(job):
    "Initialize the simulation configuration."
    import hoomd
    if hoomd.context.exec_conf is None:
        hoomd.context.initialize('')
    with job:
        with hoomd.context.SimulationContext():
            n = ceil(pow(job.sp.N, 1/3))
            assert n**3 == job.sp.N
            hoomd.init.create_lattice(unitcell=hoomd.lattice.sc(a=1.0), n=n)
            hoomd.dump.gsd('init.gsd', period=None, group=hoomd.group.all())


def estimate(job):
    "Ideal-gas estimate operation."
    sp = job.statepoint()
    # Calculate volume using ideal gas law
    V = sp['N'] * sp['kT'] / sp['p']
    job.document['volume_estimate'] = V


def sample(job):
    "Sample operation."
    import hoomd
    from hoomd import md
    if hoomd.context.exec_conf is None:
        hoomd.context.initialize('')
    with job:
        with redirect_log(job):
            with hoomd.context.SimulationContext():
                hoomd.init.read_gsd('init.gsd', restart='restart.gsd')
                group = hoomd.group.all()
                gsd_restart = hoomd.dump.gsd(
                    'restart.gsd', truncate=True, period=100, phase=0, group=group)
                lj = md.pair.lj(r_cut=job.sp.r_cut, nlist=md.nlist.cell())
                lj.pair_coeff.set('A', 'A', epsilon=job.sp.epsilon, sigma=job.sp.sigma)
                md.integrate.mode_standard(dt=0.005)
                md.integrate.npt(
                    group=group, kT=job.sp.kT, tau=job.sp.tau,
                    P=job.sp.p, tauP=job.sp.tauP)
                hoomd.analyze.log('dump.log', ['volume'], 100, phase=0)
                try:
                    hoomd.run_upto(STEPS)
                except hoomd.WalltimeLimitReached:
                    logger.warning("Reached walltime limit.")
                finally:
                    gsd_restart.write_restart()
                    job.document['sample_step'] = hoomd.get_step()
                    store_meta_data(job)


def auto(job):
    "This is a meta-operation to execute multiple operations."
    from my_project import get_project
    project = get_project()
    logger.info("Running meta operation 'auto' for job '{}'.".format(job))
    for i in range(10):
        next_op = project.next_operation(job)
        if next_op is None:
            logger.info("No next operation, exiting.")
            break
        else:
            logger.info("Running next operation '{}'...".format(next_op))
            func = globals()[next_op.name]
            func(job)
    else:
        logger.warning("auto: Reached max # operations limit!")
