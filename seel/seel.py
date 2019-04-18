# SEEL >>> the Send-Expect-Extract-Loop
#
# Copyright (C) 2019 ADVA Optical Networking
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from functools import lru_cache
import logging
import re

import modeled
from modeled import member as data

import seel
from .command import Command
from .process import Process

__all__ = ('SEEL', )


class SEEL(modeled.object):

    __package__ = seel

    class meta:
        command_type = Command

        commands = {}

        @property
        @lru_cache()
        def command(seelcls):

            class command(seelcls.command_type):

                class meta:

                    subcommands = {}

                    @property
                    @lru_cache()
                    def subcommand(cls):

                        class subcommand(seelcls.command):

                            class meta:

                                owner = None
                                subcommands = {}

                                def __init__(cls, clsname, bases, clsattrs):
                                    if cls.owner is not None:
                                        cls.owner.subcommands[clsname] = cls

                        subcommand.meta.owner = cls
                        subcommand.__module__ = cls.__module__
                        subcommand.__qualname__ = "{}.command".format(
                            cls.__qualname__)
                        return subcommand

                    def __init__(cls, clsname, bases, clsattrs):
                        if cls.owner is not None:
                            cls.owner.commands[clsname] = cls

            command.meta.owner = seelcls
            command.__module__ = seelcls.__module__
            command.__qualname__ = "{}.command".format(seelcls.__qualname__)
            return command

    class introspection:
        completion_regex = None
        command_regex = None

    encoding = data[str]()

    context = data[str](None)
    prompt = data[str](None)

    # timeout = data[float](None)

    def __init__(self, encoding='ascii'):
        super().__init__(encoding=encoding)
        self.logger = logging.getLogger(type(self).__qualname__)
        self.repl = None
        self.commands = []

    def _start_repl(self, command):
        self.commands = []
        self.repl = Process(command)

    def connect(
            self, command, prompt_regex=r"(?P<prompt>.*>)\s*$", timeout=1.0):
        self.prompt_regex = regex = re.compile(
            prompt_regex, flags=re.MULTILINE)
        self._start_repl(command)
        # self.timeout = timeout
        data = ""
        while not data or not regex.search(data):
            data += self.repl.recv(1024).decode('ascii')
        self.prompt = regex.search(data).group('prompt')
        self.logger.info("Prompt: {}".format(self.prompt))

    def introspect(self):
        cls = type(self)
        result = cls.command(seel=self, name="")._call(append="\t")

        if cls.introspection.completion_regex:
            completions = re.search(
                cls.introspection.completion_regex, result.text,
                flags=re.MULTILINE
            ).group('commands')
        else:
            completions = result.text

        if cls.introspection.command_regex:
            self.commands = [match.group('name') for match in re.finditer(
                cls.introspection.command_regex, completions,
                flags=re.MULTILINE)]
        else:
            self.commands = result.text.split()

    def raw(self, cmdname, *args):
        return Command[cmdname](seel=self)(*args)

    def __call__(self, cmdname, *args):
        try:
            cmd = self[cmdname]
        except KeyError:
            cmd = type(self).command(seel=self, name=cmdname)
        return cmd(*args)

    def __getitem__(self, cmdname):
        cls = type(self)
        cmdcls = cls.commands.get(cmdname)
        if cmdcls is None:
            if cmdname not in self.commands:
                raise KeyError(cmdname)

            return cls.command(seel=self, name=cmdname)

        if not issubclass(cmdcls, cls.command_type):
            raise TypeError(
                "Registered command class {!r} for command {!r} of {!r} "
                "is not derived from {!r}".format(
                    cmdcls, cmdname, cls, cls.command_type))

        return cmdcls(seel=self)

    def __getattr__(self, cmdname):
        if cmdname.startswith('_'):
            raise AttributeError(
                "{!r} has no attribute {!r}".format(self, cmdname))

        try:
            return self[cmdname]

        except KeyError:
            raise AttributeError(
                "{!r} has no attribute or known command {!r}"
                .format(self, cmdname))

    def __dir__(self):
        return super().__dir__() + list(type(self).commands) + self.commands
