# -*- coding=utf-8 -*-
from __future__ import unicode_literals, print_function
import subprocess
from ansible import constants
from ansible import utils
from ansible.callbacks import display
import os
import pkg_resources
import sys

__author__ = 'mgallet'


def chdir():
    """ Set the working directory *inside* the Penates package

    :return: nothing
    """
    filename = pkg_resources.resource_filename('penates', 'commands/auth_servers.yml')
    os.chdir(os.path.dirname(os.path.dirname(filename)))


def get_available_commands():
    """ List all command names
    :return:
    """
    result = [x[:-4] for x in os.listdir('commands') if x.endswith('.yml')]
    result.sort()
    return result


def penates_main():
    chdir()
    parser = utils.base_parser(
        constants=constants,
        usage="%prog playbook.yml",
        connect_opts=True,
        runas_opts=True,
        subset_opts=True,
        check_opts=True,
        diff_opts=True
    )
    parser.add_option('-t', '--tags', dest='tags', default='all',
                      help="only run plays and tasks tagged with these values")
    parser.add_option('--skip-tags', dest='skip_tags',
                      help="only run plays and tasks whose tags do not match these values")
    parser.add_option('--syntax-check', dest='syntax', action='store_true',
                      help="perform a syntax check on the playbook, but do not execute it")
    parser.add_option('--list-tasks', dest='listtasks', action='store_true',
                      help="list all tasks that would be executed")
    parser.add_option('--list-tags', dest='listtags', action='store_true',
                      help="list all available tags")
    parser.add_option('--step', dest='step', action='store_true',
                      help="one-step-at-a-time: confirm each task before running")
    parser.add_option('--start-at-task', dest='start_at',
                      help="start the playbook at the task matching this name")
    parser.add_option('--force-handlers', dest='force_handlers',
                      default=constants.DEFAULT_FORCE_HANDLERS, action='store_true',
                      help="run handlers even if a task fails")
    parser.add_option('--flush-cache', dest='flush_cache', action='store_true',
                      help="clear the fact cache")
    options, args = parser.parse_args()
    if not args:
        display('ERROR: You must specify one command to execute.', color='red', stderr=True)
        print('List of available commands:')
        for command_name in get_available_commands():
            print('  %s' % command_name)
        return 1
    elif len(args) > 1:
        display('ERROR: You can specify only one command.', color='red', stderr=True)
        return 2
    elif args[0] not in get_available_commands():
        display('ERROR: "%s" is not an available command.' % args[0], color='red', stderr=True)
        return 3
    command_name = args[0]
    command = ['ansible-playbook', 'commands/%s.yml' % command_name] + [x for x in sys.argv[1:] if x != command_name]
    p = subprocess.Popen(command)
    p.communicate()
    return p.returncode

if __name__ == "__main__":
    sys.exit(penates_main())
