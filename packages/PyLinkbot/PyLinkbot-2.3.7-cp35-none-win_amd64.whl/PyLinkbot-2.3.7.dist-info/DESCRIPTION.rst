PyLinkbot
=========

PyLinkbot - A Python package for controlling Barobo Linkbots
Contact: David Ko <david@barobo.com>

Linkbots are small modular robots designed to play an interactive role in
computer science and mathematics curricula. More information may be found at
http://www.barobo.com .

Requirements
------------

This package is built against Python 3.4 . Python 2 is explicitely not
supported, and other versions of Python 3 may or may not work. Additionally,
the SciPy <http://www.scipy.org> is highly recommended for graphical plotting
and more.

Installation
------------

The recommended way to install this package is through setuptools utilities,
such as "easy_install" or "pip". For example:

    easy_install3 PyLinkbot

or

    pip3 install PyLinkbot

Building
--------

As of version 2.3.2, building from the setup.py script has been tested on Ubuntu
14.04 LTS. The requirements to build this package are:

    cmake
    git
    python3-dev
    gcc
    g++

To install all of these at once, run the command:

    sudo apt-get install cmake git python3-dev gcc g++

Next, you should be able to run the setup script.

    python3 setup.py build

The script will download and build all necessary dependencies, including Boost
and the Linkbot Labs SDK package. Please note that the building process can take
quite a bit of time to complete, and there is currently minimal UI feedback
during the process, so patience is appreciated. 


2.3.7
=====
- Fixed bug on some systems when using a button event callback function.
- Added "move_joint_accel" functions

2.3.6
=====
- Added PEP8 compliant member function names. i.e. move_wait() instead of
  moveWait()

2.3.2
=====
- Compiled against Linkbot Labs 1.0.3
- Added functions to control the acceleration/deceleration of Linkbot
  Motors. See Linkbot.moveSmooth() family of functions. These functions will
  only work on Linkbot Firmware versions higher than 4.4.4.

2.3.1
=====
- Compiled against Linkbot Labs 0.9.1

2.3.0
=====
- Updated to Linkbot Labs 0.7.9 library.
- Changed robot radio communications protocol. It is now possible to "hot-swap"
  dongles and maintain connections to previously connected robots. However, the
  new protocol is not backwards compatible. If you are using Linkbot Labs 0.7.6
  or 0.7.7, please use the PyLinkbot 2.2.2 .

2.2.2
=====
- Updated to Linkbot Labs 0.7.7 library. 
- Changed moveWait() to pure Python function.

2.2.1
=====
- Fixed deadlock; Module would sometimes deadlock if main thread called an RPC
  function while an event handler callback function was executing.

2.2.0
=====
- Built against new Linkbot Labs 0.7.6

2.1.3
=====
- Added missing dlls

2.1.2
=====
- Added functions to access TWI
- Added functions to access Linkbot Arduino shield
- Fixed an exception-on-exit

2.1.1
=====
- Improved robustness of moveWait().

2.1.0
=====
- Added functions setMotorPower() and moveJointTo()

2.0.4
=====
- Python module no longer disables robot broadcasts on disconnect unless they
  were enabled by this module in the first place.

2.0.3
=====
- Internal bugfixes; Renamed some C++ API functions

2.0.2
=====
- Fixed getAccelerometer() member function.

2.0.1
=====
- Made serial ID case insensitive.
- Fixed race condition/deadlock when waiting for joints to finish moving.

2.0.0
=====
- Refactored back-end from PyBarobo (v1.0.0 series) to work with the new
  LinkbotLabs and baromesh protocol.



