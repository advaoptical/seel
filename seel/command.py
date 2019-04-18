from functools import lru_cache
import re

import modeled
from modeled import member as data

__all__ = ('Command', )


class Command(modeled.object):

    class meta:

        owner = None

        @lru_cache()
        def __getitem__(cls, cmdname):
            return type(cmdname, (cls, ), {
                '__module__': cls.__module__,
                '__qualname__':
                    "{}[{!r}]".format(cls.__qualname__, cmdname)})

    class result(modeled.object):

        text = data[str]()

        def __repr__(self):
            return self.text

    def __init__(self, seel, name=None):
        self.seel = seel
        if name is None:
            name = type(self).__name__
            owner = type(self).owner
            while owner is not None and issubclass(owner, Command):
                name = " ".join((owner.__name__, name))
                owner = owner.owner
        self.__name__ = name
        self.subcommands = []

    def __call__(self, *args):
        return self._call(args)

    def _call(self, args=None, append="\n"):
        command = self.__name__
        if args is not None:
            command += " {}".format(" ".join(map(str, args)))
        command_regex = re.compile(r"^\s*{}".format(re.escape(command)))
        command += append
        self.seel.repl.send(command.encode(self.seel.encoding))

        expect_regex = getattr(type(self), 'expect', None)
        if expect_regex is not None:
            expect_regex = re.compile(expect_regex, flags=re.MULTILINE)
        prompt_regex = self.seel.prompt_regex
        # prompt_regex = re.compile(
        #     r"{}\s*$".format(re.escape(self.seel.prompt)),
        #     flags=re.MULTILINE)

        # read text until next prompt appears
        text = ""
        while not text or not prompt_regex.search(text) or (
                expect_regex and not expect_regex.search(text)):
            text += self.seel.repl.recv(1024).decode(self.seel.encoding)

        # remove sent command
        text = command_regex.sub("", text)
        text = re.sub(r"^(\s*\n)?([^\S\n]*)", r"\2", text, flags=re.MULTILINE)
        # extract next prompt and context
        prompt_data = prompt_regex.search(text).groupdict()
        text = prompt_regex.sub("", text)
        self.seel.prompt = prompt_data['prompt']
        if 'context' in prompt_data:
            self.seel.context = prompt_data['context']
            self.seel.logger.info("Context: {}".format(self.seel.context))
        self.seel.logger.info("Prompt: {}".format(self.seel.prompt))
        return type(self).result(text=re.sub(r"\n\s*$", "\n", text))

    def __getitem__(self, subcmdname):
        cls = type(self)
        seelcls = type(self.seel)

        subcmdcls = cls.subcommands.get(subcmdname)
        if subcmdcls is None:
            if subcmdname not in self.subcommands:
                raise KeyError(subcmdname)

            return cls.subcommand(seel=self.seel, name=subcmdname)

        if not issubclass(subcmdcls, seelcls.command_type):
            raise TypeError(
                "Registered subcommand class {!r} for command {!r} of {!r} "
                "is not derived from {!r}".format(
                    subcmdcls, subcmdname, cls, seelcls.command_type))

        return subcmdcls(seel=self.seel)

    def __getattr__(self, subcmdname):
        if subcmdname.startswith('_'):
            raise AttributeError(
                "{!r} has no attribute {!r}".format(self, subcmdname))

        try:
            return self[subcmdname]

        except KeyError:
            raise AttributeError(
                "{!r} has no attribute or known command {!r}"
                .format(self, subcmdname))

    def __dir__(self):
        return super().__dir__() + (
            list(type(self).subcommands) + self.subcommands)

    def __repr__(self):
        return "<seel.Command {!r} of {!r}>".format(self.__name__, self.seel)
