#! /usr/bin/python
import argparse
import os
import sys
from ConfigParser import SafeConfigParser
from collections import OrderedDict
from subprocess import call
import textwrap


class Command(object):

    def init(self, args):
        self.args = args
        self.loc = self.expand_path('~/.vcd')
        self.cfg = self.load_config()

    def expand_path(self, path):
        path = os.path.expanduser(path)
        path = os.path.expandvars(path)
        path = os.path.abspath(path)
        return path

    def load_config(self):
        """Returns a dictionary representation of the current config file."""
        cp = SafeConfigParser()
        cp.read(self.loc)
        cfg = OrderedDict()

        for section in ['venvs', 'cmd_map']:
            cfg[section] = OrderedDict()
            if cp.has_section(section):
                for k in cp.options(section):
                    cfg[section][k] = cp.get(section, k)
        return cfg

    def write_cfg(self):
        """Writes the current self.cfg dictionary to the default config file
        location as a config file, overwriting anything already in the config.
        """
        cp = SafeConfigParser()
        for section in ['venvs', 'cmd_map']:
            cp.add_section(section)
            for k, v in self.cfg[section].iteritems():
                cp.set(section, k, value=v)
        fp = open(self.loc, "w")
        cp.write(fp)
        fp.close()


class register_venv(Command):
    def __init__(self, args):
        self.init(args)
        loc = self.expand_path(self.args.location)
        self.cfg['venvs'].update({self.args.name: loc})
        self.write_cfg()


class register_cmd(Command):
    def __init__(self, args):
        self.init(args)
        if self.args.venv_alias not in self.cfg['venvs'].keys():
            sys.exit(
                "Could not register command: no virtualenv has been registered"
                " with the name {venv}".format(venv=self.args.venv_alias))
        cmd_str = self.args.venv_alias
        if self.args.command:
            cmd_str = "{venv},{cmd}".format(
                venv=self.args.venv_alias, cmd=self.args.command)
        self.cfg['cmd_map'].update({self.args.command_alias: cmd_str})
        self.write_cfg()


class list_resources(Command):
    def __init__(self, args):
        self.init(args)
        resource = args.resource
        resource_name = 'cmd_map' if resource == 'cmds' else resource
        resources = self.cfg.get(resource_name, {})
        k_justify = len(max(resources.keys(), key=len))
        v_justify = len(max(resources.values(), key=len))

        print "\n{0:^{1}} @ {2:^{3}}".format(
            resource_name, k_justify, "location", v_justify)
        print "-"*(k_justify+v_justify+3)
        for k, v in resources.iteritems():
            print "{0:<{1}} @ {2:<{3}}".format(k, k_justify, v, v_justify)


class exec_cmd(Command):
    def __init__(self, args):
        self.init(args)
        if not args.command:
            sys.exit("No command provided")
        cmd = args.command[0]
        remainder = " ".join(args.command[1:])
        info = self.cfg['cmd_map'].get(cmd).split(',')
        venv_loc = os.path.expanduser(self.cfg['venvs'].get(info[0]))
        if len(info) > 1:
            cmd = info[1]
        cmd_str = ". {venv_loc}/bin/activate; {cmd} {rmdr}".format(
            venv_loc=venv_loc, cmd=cmd, rmdr=remainder)
        call(
            cmd_str, stdout=sys.stdout, stderr=sys.stderr, shell=True)


def vcd_run():
    """ This is a seperate entry point to avoid colisions between vcd
    options and possible command aliases entered by the user"""
    parser = argparse.ArgumentParser()

    # Read the config and set the current commands as argaprser options
    cmd = Command()
    cmd.init(list())
    cmds = cmd.cfg['cmd_map'].keys()
    cmds.sort()
    padded_cmds = " ".join([x.ljust(len(max(cmds, key=len))) for x in cmds])
    parser.add_argument(
        'command', type=str, choices=cmds, nargs=argparse.REMAINDER,
        metavar="\n" + textwrap.fill(padded_cmds))
    parser.set_defaults(func=exec_cmd)

    # parse args and trigger actions
    args = parser.parse_args()
    args.func(args)


def vcd_config():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(metavar="add, list")

    # Registration subparsers
    register_parser = subparsers.add_parser(
        "add", usage="\n  Add new venvs and commands to vcd")
    register_subparsers = register_parser.add_subparsers(metavar="venv, cmd")

    # register venv <name> <location>
    register_venv_sparser = register_subparsers.add_parser("venv")
    register_venv_sparser.add_argument(
        'venv_alias', type=str, help="An alias used to address the virtualenv")
    register_venv_sparser.add_argument(
        'path_to_venv_dir', type=str,
        help="Location of the virtualenv top level directory")
    register_venv_sparser.set_defaults(func=register_venv)

    # register command <name> <location>
    register_venv_sparser = register_subparsers.add_parser("cmd")
    register_venv_sparser.add_argument(
        'venv_alias', type=str, help="An alias used to address the virtualenv")
    register_venv_sparser.add_argument(
        'command_alias', type=str,
        help="An alias used to trigger the registered command.  The actual "
        "command can be used here.")
    register_venv_sparser.add_argument(
        'command', nargs='?', default='', type=str,
        help="Optional.  If omitted, it is assumed that the command-alias is "
        "the as the actual command")
    register_venv_sparser.set_defaults(func=register_cmd)

    # Listing subparsers
    list_parser = subparsers.add_parser(
        "list", usage="\n  List registered venvs and commands")
    list_parser.add_argument(
        'resource', type=str, choices=['venvs', 'cmds'], metavar="venvs, cmds")
    list_parser.set_defaults(func=list_resources)

    args = parser.parse_args()
    args.func(args)
