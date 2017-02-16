#!/usr/bin/env python
"Submit job-operations to a scheduler."
import argparse
import logging

from .project import get_project
from . import environment


def main(env, args):
    args.mode = 'gpu' if args.gpu else 'cpu'

    project = get_project()
    project.submit(env, **vars(args))


if __name__ == '__main__':
    env = environment.get_environment()
    parser = argparse.ArgumentParser()
    get_project().add_submit_args(parser)
    group = parser.add_argument_group(
        "Execution configuration:",
        "Specify the execution environment.")
    group.add_argument(
        '--gpu',
        action='store_true',
        help="Specify to use the GPU execution mode.")
    group.add_argument(
        '--np',
        type=int,
        default=1,
        help="Specify the total # of processors to be used per operation.")
    group.add_argument(
        '--ppn',
        type=int,
        default=getattr(env, 'cores_per_node', None),
        help="Specify the number of processors allocated to each node.")
    args = parser.parse_args()

    if args.ppn is None:
        raise ValueError(
            "Did not find a default value for the processors-per-node (ppn)."
            "Please provide `--ppn` argument")
    logging.basicConfig(level=logging.INFO)
    main(env, args)
