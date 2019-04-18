# from subprocess import PIPE, Popen, STDOUT
import asyncio
import locale
import os
import sys
from asyncio.subprocess import PIPE, STDOUT
from contextlib import closing

__all__ = ('Process', )


class SubprocessProtocol(asyncio.SubprocessProtocol):
    def pipe_data_received(self, fd, data):
        if fd == 1: # got stdout data (bytes)
            print(data)

    def connection_lost(self, exc):
        loop.stop() # end loop.run_forever()


class Process:

    async def readline_and_kill(self, command):
        if os.name == 'nt':
            loop = asyncio.ProactorEventLoop() # for subprocess' pipes on Windows
            asyncio.set_event_loop(loop)
        else:
            loop = asyncio.get_event_loop()
        try:
            loop.run_until_complete(loop.subprocess_exec(SubprocessProtocol,
                *command))
            loop.run_forever()
        finally:
            loop.close()

    def __init__(self, command):
        # self._process = Popen(
        #     command, stdin=PIPE, stdout=PIPE, stderr=STDOUT)

        if sys.platform == "win32":
            loop = asyncio.ProactorEventLoop()
            asyncio.set_event_loop(loop)
        else:
            loop = asyncio.get_event_loop()

        with closing(loop):
            loop.run_until_complete(self.readline_and_kill(command))

    def send(self, text):
        self._process.stdin.write(text)

    def recv(self, size):
        return self._process.stdout.read(size)

    def close(self):
        self._process.terminate()
