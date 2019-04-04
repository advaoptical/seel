SEEL >>> the Send-Expect-Extract-Loop
=====================================

### A Pythonic approach to remotely control REPLs

And what is a REPL? A **R**ead-**E**valuate-**P**rint-**L**oop!
Also called Command Line Interface (CLI)

<a href="https://advaoptical.com">
  <img
    alt="ADVA Optical Networking"
    src="https://www.advaoptical.com/-/media/adva-main-site/logo.ashx"
    width="256"
    >
</a>

SEEL is a **Free** OpenSource project of [
  ADVA Optical Networking][advaoptical]

[advaoptical]: https://advaoptical.com

> **Licensed** under the [Apache License, Version 2.0][license]

[license]: http://www.apache.org/licenses/LICENSE-2.0

> SEEL is [MODELED][modeled] >>> **M**ODELED **O**bjects **D**amn **E**sily
> **L**oad and **E**mit **D**ata

[modeled]: https://github.com/modeled

The SEEL API attempts to make the following tasks as simple as possible:

* Spawn a local CLI or connect to a remote CLI through SSH
* Send commands to the CLI and verify their returned output with Regular
  Expressions
* Specify Pythonic APIs for those commands
* Extract relevant data from their output via Regular Expressions and turn
  them into useful Python data types and structures
