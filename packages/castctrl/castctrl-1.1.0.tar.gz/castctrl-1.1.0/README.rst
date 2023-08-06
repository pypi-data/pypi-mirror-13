castctrl
========

A Python program to simplify casting video to a Chromecast

Usage
-----

::

    usage: castctrl [-h] [--url URL] [--power] [-s] [-d DEVICE] [-D] [--port PORT]

    optional arguments:
      -h, --help            show this help message and exit
      --url URL             URL of media to play. You should probably specify this
                            if nothing else
      --power               Turn on TV and switch to Chromecast
      -s, --stop            Stop playback
      -d DEVICE, --device DEVICE
                            Select device. List devices with -D
      -D, --devices         List devices
      --port PORT           Specify port for web server (if you pick a local file
                            above)

Installation
------------

Via ``pip``:

::

    pip3 install castctrl

Alternatively:

-  Clone the repository, ``cd castctrl``
-  Run ``python3 setup.py install`` or ``pip3 install -e``
