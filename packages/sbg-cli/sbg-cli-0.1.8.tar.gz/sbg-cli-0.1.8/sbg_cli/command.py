__author__ = 'Sinisa'


import re
import inspect
import importlib


def get_commands(module):
    modules = module.__all__
    commands = {}
    for m in modules:
        if not m.startswith('__'):
            mem = importlib.import_module(module.__name__ + '.' + m)
            for name, obj in inspect.getmembers(mem):
                if inspect.isclass(obj) and Command in obj.__bases__:
                    o = obj()
                    commands[o.cmd] = o
    return commands


def create_command(basecommand, cmd):
    return '\t{basecmd} {cmd} {args}\n'.format(basecmd=basecommand, cmd=cmd.cmd, args=cmd.args)


def create_usage_string(usage, basecommand, cmds):
    cmds_ordered = sorted([cmd for cmd in cmds.values()], key = lambda x: x.order)
    usg = ''
    for cmd in cmds_ordered:
        usg = usg + create_command(basecommand, cmd)
    usage = usage.format(usage=usg)
    return usage


def get_utils(module, basecmd):
    modules = module.__all__
    utils = []
    for m in modules:
        mem = importlib.import_module(m)
        utility = importlib.import_module(mem.__utility__)
        for name, obj in inspect.getmembers(utility):
            if inspect.isclass(obj) and Utility in obj.__bases__:
                utils.append(obj(basecmd))
    return utils


def sbg_usage(utils):
    usg = None
    for u in utils:
        if not usg:
            usg = '{}'.format(u.usage)
        else:
            usg = '{usg}\n{utility}'.format(usg=usg, utility=u.usage)
    return usg


def verbosity(args):
    '''
    :param args:
    :return:
    >>> verbosity(["-vvvv", "--verbose", "something"])
    Traceback (most recent call last):
        ...
    DocoptExit
    >>> verbosity([ "command", "-v", "argument1"])
    (1, ['command', 'argument1'])
    >>> verbosity([ "command", "-vvvv", "argument1"])
    (4, ['command', 'argument1'])
    >>> verbosity([ "command", "--verbose", "--verbose", "argument1"])
    (2, ['command', 'argument1'])
    >>> verbosity(["command", "argument1"])
    (0, ['command', 'argument1'])
    '''
    v = filter(lambda x: re.match("^-[v]{1,5}$", x), args)
    verb = filter(lambda x: x == '--verbose', args)
    rest = filter(lambda x: not (re.match("^-[v]{1,5}$", x) or x == '--verbose'), args)
    if all([v, verb]):
        raise Exception
    if v:
        if len(v) > 1:
            return len(v), rest
        else:
            return v[0].count('v'), rest
    elif verb:
        return len(verb), rest
    return 0, rest


class Utility(object):

    USAGE = '''{usage}'''

    def __init__(self, basecmd):
        self.basecmd = basecmd
        self.commands = {}

    @property
    def usage(self):
        return self.USAGE

    @property
    def command_list(self):
        return self.commands.keys()


class Command(object):

    cmd = ''
    args = ''
    order = 0


if __name__ == '__main__':
    import doctest
    doctest.testmod()
