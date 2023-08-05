#!/usr/bin/env python3
# coding: utf-8

from __future__ import unicode_literals, print_function
import sys
from molbiox.frame.command import Command


class CommandXP(Command):
    abbr = 'xp'
    name = 'xperiment'
    desc = 'experiment with command facilities'

    @classmethod
    def register(cls, subparser):
        subparser = super(cls, cls).register(subparser)
        subparser.add_argument(
            '-x', '--xp', metavar='character', type=int,
            help="seperator used on subject names")
        return subparser

    @classmethod
    def render(cls, args, outfile):
        print(type(args.xp), args.xp)
