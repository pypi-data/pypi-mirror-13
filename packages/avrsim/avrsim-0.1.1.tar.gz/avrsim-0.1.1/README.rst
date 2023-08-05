AVR Simulator
#############

..  image:: https://img.shields.io/travis/rblack42/avrsim.svg

..  image:: https://coveralls.io/repos/rblack42/avrsim/badge.svg?branch=master&service=github 
    :target: https://coveralls.io/github/rblack42/avrsim?branch=master
    :alt: Coverage Status
    
..  image:: https://img.shields.io/pypi/v/avrsim.svg
    :target: https://pypi.python.org/pypi/avrsim/
    :alt: Latest Version
     
..  image:: https://img.shields.io/pypi/l/avrsim.svg
    :target: http://pypi.python.org/pypi/avrsim/
    :alt: License

..  image:: https://img.shields.io/pypi/pyversions/avrsim.svg
    :target: https://pypi.python.org/pypi/avrsim/
    :alt: Supported Python versions

This project is designed to build a simulator for the Arduino Uno processor use
din projects in my COSC2325 COmputer Architecture and Machine Language class at
Austin Community COllege.

The project is written in Python (tested on py2.7 and py3.5). It uses the MyHDL
hardware description library to build a simulation thta cna be converted to
real hardware using an FPGA. The current project targets the Basys3 (Artix 7
FPGA) board produced by `Digilent <http://www.diginentinc.com>`_.

