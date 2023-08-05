AVR Simulator
#############

..  image:: https://img.shields.io/travis/rblack42/AVRsim.svg

..  image:: https://coveralls.io/repos/rblack42/AVRsim/badge.svg?branch=master&service=github 
    :target: https://coveralls.io/github/rblack42/AVRsim?branch=master
    :alt: Coverage Status
    
..  image:: https://img.shields.io/pypi/v/AVRsim.svg
    :target: https://pypi.python.org/pypi/avrsim/
    :alt: Latest Version
     
..  image:: https://img.shields.io/pypi/l/AVRsim.svg
    :target: http://pypi.python.org/pypi/avrsim/
    :alt: License

..  image:: https://img.shields.io/pypi/pyversions/AVRsim.svg
    :target: https://pypi.python.org/pypi/avrsim/
    :alt: Supported Python versions

This project is designed to build a simulator for the Arduino Uno processor
used in projects in my COSC2325 `Computer Architecture and Machine Language`
class at Austin Community College.

The project is written in Python (tested on py2.7 and py3.5). It uses the MyHDL
hardware description library to build a simulation that can be converted to
real hardware using an FPGA. The current project targets the Basys3 (Artix 7
FPGA) board produced by `Digilent <http://store.digilentinc.com/>`_.

For more information on the project, contact the author::

    Roie Black
    Professor, Computer Science
    Austin Community College
    Austin, Texas

    email: rblack@austincc.edu
    web: www.austincc.edu/rblack
    GitHub: http://github.com/rblack42/AVRsim

..  vim:filetype=rst spell:
