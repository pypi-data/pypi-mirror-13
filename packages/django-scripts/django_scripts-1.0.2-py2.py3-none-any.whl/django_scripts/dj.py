#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2007-2015, Raffaele Salmaso <raffaele@salmaso.org>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from __future__ import absolute_import, division, print_function, unicode_literals
import sys
import os
from os.path import dirname
from stua.commands import BaseCommand
from stua.os import system


class Command(BaseCommand):
    def find_manage_py(self, path=None):
        path = path or os.getcwd()

        while path != '/':
            manage = os.path.join(path, 'manage.py')
            if os.path.exists(manage):
                return path
            path = dirname(path)
        return False

    def build_cmd(self, command, args):
        cmd = []

        command = command.split('/')[-1]
        try:
            cmd.append({"dj2": "python2", "dj3": "python3"}[command])
        except:
            pass

        cmd.append("./manage.py")

        if len(args) > 0:
            if args[0] == 'test':
                # test are always verbose if not tell otherwise
                verbosity = [True for arg in args if arg.startswith("--verbosity")]
                if not verbosity:
                    args.append('--verbosity=2')
        cmd.extend(args)

        return cmd

    def handle(self, command, args):
        path = self.find_manage_py()

        status = 0
        if path:
            os.chdir(path)
            cmd = self.build_cmd(command, args)
            status = system(*cmd)
        return status


def main():
    dj = Command()
    status = dj.run(sys.argv)
    sys.exit(status)
