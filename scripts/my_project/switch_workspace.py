#!/usr/bin/env python
"""Manage multiple workspaces to seperate different stages of your work."""
import sys
import os
import logging
import argparse

import signac


logger = logging.getLogger(__name__)

WORKSPACES = {
    'main': 'workspace',
    'debug': 'workspace_debug',
}


def main(args):
    config = signac.common.config.read_config_file(args.config)
    try:
        config['workspace_dir'] = WORKSPACES[args.workspace]
    except KeyError:
        raise ValueError(
            "Unknown workspace '{}'.".format(args.workspace))
    config.write()
    print("Switched to workspace '{}'.".format(config['workspace_dir']))
    return 0

if __name__ == '__main__':
    project = signac.get_project()
    parser = argparse.ArgumentParser(
        description="Switch between different workspace.")
    parser.add_argument(
        'workspace',
        type=str,
        choices=list(WORKSPACES.keys()),
        help="The workspace to activate.")
    parser.add_argument(
        '-c', '--config',
        type=str,
        default=os.path.join(project.root_directory(), 'signac.rc'),
        help="The config file to manipulate.")
    args = parser.parse_args()
    logging.basicConfig(level=logging.WARNING)
    sys.exit(main(args))
