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
import os
from os.path import dirname
import sys

from stua.commands import ArgumentCommand
from stua.os import system


class RunServer(object):
    def __init__(self, **opts):
        for k, v in opts.items():
            setattr(self, k, v)

    def start(self, options, args):
        if "--noinsecure" in args:
            args.remove("--noinsecure")
        else:
            args.append("--insecure")

        status = 0
        path = self.path
        while path != '/':
            manage = os.path.join(path, 'manage.py')
            if os.path.exists(manage):
                os.chdir(path)
                cmd = []
                try:
                    cmd.append({"rs2": "python2", "rs3": "python3"}[self.command])
                except:
                    pass
                cmd.extend([manage, 'runserver', "{}:{}".format(self.addr, self.port)])
                cmd.extend(args)
                status = system(*cmd)
            path = dirname(path)
        return status


class ServerCommand(ArgumentCommand):
    help = "run ./manage.py runserver"

    def add_arguments(self, parser):
        parser.add_argument(
            "-a", "--addr",
            action="store",
            dest="addr",
            default="0.0.0.0",
            help="bind address",
        )
        parser.add_argument(
            "-p", "--port",
            action="store",
            dest="port",
            type=int,
            default=8000,
            help="port",
        )
        parser.add_argument(
            "-9",
            action="store_true",
            dest="use_port_9000",
            help="use port=9000",
        )

    def handle(self, command, options, args):
        command = command.split('/')[-1]
        addr = options.get("addr")
        port = options.get("port")
        if (options.get("use_port_9000")):
            port = 9000
        path = os.getcwd()

        server = RunServer(command=command, addr=addr, port=port, path=path)
        return server.start(options, args)


def main():
    cmd = ServerCommand()
    status = cmd.run(sys.argv)
    sys.exit(status)
