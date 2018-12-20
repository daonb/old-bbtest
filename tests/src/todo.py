#!/usr/bin/env python
# encoding: utf-8
"""
Python based implementation for todo.sh (https://github.com/todotxt/todo.txt-cli)
"""

import os
import sys
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter


version = 0.1


todo_file = os.path.join(os.path.dirname(__file__), 'todo.txt')


def main(args=None):

    """ A simple and extensible script for managing your todo.txt file. """
    program_version = "v%s" % version
    program_version_message = '%%(prog)s %s' % (program_version)
    description = '''A simple and extensible script for managing your todo.txt file.'''

    # Setup argument parser
    parser = ArgumentParser(description=description,
                            formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument('-V', '--version', action='version', version=program_version_message)

    subparsers = parser.add_subparsers(help='type "todo [subcommand] -h" for help.')

    # add sub-parser
    add_convert = subparsers.add_parser('add', formatter_class=ArgumentDefaultsHelpFormatter)
    add_convert.set_defaults(func=add_todo)
    add_convert.add_argument('todo', nargs=1, metavar='todo',
                              help='Add todo to the end of the list')

    # load sub-parser
    load_analyze = subparsers.add_parser('list', formatter_class=ArgumentDefaultsHelpFormatter)
    load_analyze.set_defaults(func=list_todos)

    # Process arguments
    parsed_args = parser.parse_args(args)

    parsed_args.func(parsed_args)


def add_todo(parsed_args):

    with open(todo_file, 'a+') as f:
        f.write(f'{parsed_args.todo[0]}\n')


def del_todo(parsed_args):

    with open(todo_file, 'r+') as f:
        todos = f.readlines()
    todos.remove(parsed_args.todo)
    with open(todo_file, 'w+') as f:
        f.writelines(todos)


def list_todos(parsed_args):

    with open(todo_file, 'r+') as f:
        todos = f.readlines()
    for todo in todos:
        print(todo.strip())


if __name__ == "__main__":
    sys.exit(main((sys.argv[1:])))