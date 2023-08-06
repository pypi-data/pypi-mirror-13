RPi.Doorman Gammu
#################

Door state monitor, with ability to make a phone call completely written in Python.

.. image:: https://badge.fury.io/py/rpi-doorman-gammu.png
    :target: http://badge.fury.io/py/rpi-doorman-gammu

This is just and extension for RPi.Doorman project to support python-gammu. With aditional dependencies this project allows to make a phone calls when sensor state changes.

For more information check `rpi-doorman <https://github.com/ricco386/rpi-doorman/>`_ project.


Installation
------------

- Install the latest released version using pip::

      pip install https://github.com/ricco386/rpi-doorman-gammu/zipball/master

- Make sure all dependencies (listed below) are installed (done automatically when installing via pip)
- The ``rpi-doorman-gammu`` command should be installed somewhere in your ``PATH``.
- Systemd scripts are available: https://github.com/ricco386/rpi-doorman-gammu/tree/master/init.d

Systemd scripts should be run under **default Raspberry Pi user** (pi) so scripts can access GPIO. 


**Dependencies:**

- `RPi.GPIO <https://pypi.python.org/pypi/RPi.GPIO>`_ (0.6.1+)
- `rpi-doorman <https://pypi.python.org/pypi/rpi-doorman>`_ (1.1+)
- `gammu <https://github.com/gammu/gammu>`_ and `python-gammu <https://github.com/gammu/python-gammu>`_ (``sudo apt-get install gammu python-gammu``)


License
-------

For more information see the `LICENSE <https://github.com/ricco386/rpi-doorman-gammu/blob/master/LICENSE>`_ file.
