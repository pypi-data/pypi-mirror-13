tasque
======

Command-line task handler with Trello integration

Installation
------------

From the project root directory::

    $ python setup.py install

Or from pip::

    $ pip install tasque

After install, run the install script which sets up your app key (required to run) and follow the directions::

    $ tasque-install

Usage
-----

Simply run the shell::

    $ tasque-shell

For help on commands::

    > help
    > help cd
    > help ls
    ...


Release Notes
-------------

:0.4.4:
    - cd without args goes to root
    - cd /4/4/ no longer goes into /4/4/0
    - pwd shows full name path (present working directory)
    - fixed bug where cd Board wouldn't work because it wasn't lowercased
:0.4.3:
    In PyPI, with accurate README
    bug: Will still display 0.4.2 in tasque-shell
:0.0.1:
    Project created
