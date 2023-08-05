berkeley500A
============
This is an API for the Berkeley Nucleonics Corp Modell 500 A Digital Delay Generator

Author: Markus J Schmidt

Version: 0.1.0

class berkeley500AError
-----------------------
Exception class is raised

class berkeley500A
------------------
Class object for the delay generator.

Example
-------

::

    comPort = 'COM1'
    delayGen = berkeley500A(comPort)
    print(delayGen.gate)
    print(delayGen.getEcho())
