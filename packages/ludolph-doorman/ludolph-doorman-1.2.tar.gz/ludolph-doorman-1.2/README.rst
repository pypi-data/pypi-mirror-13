ludolph-doorman
###############

`Ludolph <https://github.com/erigones/Ludolph>`_: Doorman plugin

Plugin for Ludolph to be able to use `RPi.doorman <https://github.com/ricco386/rpi-doorman>`_ library on Raspberry Pi.

.. image:: https://badge.fury.io/py/ludolph-doorman.png
    :target: http://badge.fury.io/py/ludolph-doorman


Installation
------------

- Install the latest released version using pip::

    pip install ludolph-doorman

- Add new plugin section into Ludolph configuration file::

    [ludolph_doorman.serve]

- Update Ludolph to run as a default user (pi), as it needs access to GPIO
- Reload Ludolph::

    sudo systemctl restart ludolph.service


**Dependencies:**

- `Ludolph <https://github.com/erigones/Ludolph>`_ (0.6.0+)
- `RPi.doorman <https://github.com/ricco386/rpi-doorman>`_ (0.1.0+) 


License
-------

For more information see the `LICENSE <https://github.com/erigones/ludolph-doorman/blob/master/LICENSE>`_ file.

