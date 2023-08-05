__author__ = 'Sinisa'

import inject
import docopt
import sbg_cli
from sbg_cli.context import Context
from sbg_cli import __version__, disable_warnings
from sbg_cli.command import get_utils, sbg_usage, verbosity


BASECOMMAND = 'sbg'
BASECOMMAND_CGC = 'cgc'
NAME = "Seven Bridges Genomics Utilities."
NAME_CGC = "CGC Command Line Utilities"

USAGE = '''
{name}

Usage:
{usage}

Options:
    -h --help             Show this help message.
    --version             Print version and exit.
'''


def main():
    disable_warnings()
    utils = get_utils(sbg_cli, BASECOMMAND)
    usage = USAGE.format(name=NAME, usage=sbg_usage(utils))
    try:

        args = docopt.docopt(usage, version=__version__)
        for u in utils:
            for cmd in u.commands:
                if args[cmd]:
                    u(cmd, **args)
    except docopt.DocoptExit:
        print(usage)


def cgc_main():
    disable_warnings()
    utils = get_utils(sbg_cli, BASECOMMAND_CGC)
    usage = USAGE.format(name=NAME_CGC, usage=sbg_usage(utils))
    ctx = inject.instance(Context)
    ctx.usage = usage
    try:
        args = docopt.docopt(ctx.usage, version=__version__, help=False)
        for u in utils:
            for cmd in u.commands:
                if args[cmd]:
                    u(cmd, **args)
    except docopt.DocoptExit:
        print(ctx.usage)

if __name__ == '__main__':
    cgc_main()
