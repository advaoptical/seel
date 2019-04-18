import logging
import re

import paramiko

import seel
from .seel import SEEL

__all__ = ('SSH', )


class SSH(SEEL):

    __package__ = seel

    __qualname__ = 'SEEL.SSH'

    _ssh = None

    def connect(
            self, host, ssh_port=22, user='admin', password='CHGME.1a',
            prompt_regex=r"(?P<prompt>.*\n.*>)\s*$", timeout=1.0):

        if self.repl is not None and not self.repl.closed:
            self.logger.info("Closing SSH shell")
            self.repl.close()
        if self._ssh is not None and self._ssh.get_transport():
            self.logger.info("Closing SSH connection")
            self._ssh.close()

        self.prompt_regex = regex = re.compile(
            prompt_regex, flags=re.MULTILINE)
        self._ssh = ssh = paramiko.SSHClient()
        ssh.load_system_host_keys()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.logger.info("Opening SSH connection")
        ssh.connect(
            host, port=int(ssh_port), username=user, password=password)

        self.logger.info("Invoking SSH shell")
        self.repl = ssh.invoke_shell()
        self.timeout = timeout
        text = ""
        while not text or not regex.search(text):
            text += self.repl.recv(1024).decode(self.encoding)

        prompt_data = regex.search(text).groupdict()
        self.prompt = prompt_data['prompt']
        if 'context' in prompt_data:
            self.context = prompt_data['context']
            self.logger.info("Context: {}".format(self.context))
        self.logger.info("Prompt: {}".format(self.prompt))

    @property
    def timeout(self):
        return self.repl.timeout

    @timeout.setter
    def timeout(self, seconds):
        self.repl.timeout = seconds
