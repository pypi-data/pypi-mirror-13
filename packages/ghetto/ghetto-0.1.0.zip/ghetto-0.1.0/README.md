ghetto
======

A tool for (automatized) torrent files downloading from RSS feeds to use
with torrent clients which don't have built-in RSS functionality.


Requirements
------------

Python 2.7 with `pip` package manager.

Tested under MacOS X and Debian Linux.


Installation
------------

    pip install ghetto

or

    git clone https://github.com/infinite-library/ghetto.git ghetto
    cd ghetto
    python setup.py install


Usage
-----

All available options can be shown using ``ghetto`` command without any
parameters. After creation of a new configuration it is automatically added to
crontab of the current user to fetch feed time to time.

Only those torrent files which titles are passing filters and aren't passing
blacklist are downloaded. Comments started from ``#`` character and empty lines
allowed.

Example of filters list:

```
# Some ongoings by HorribleSubs
HorribleSubs*Heavy*Object*720p
HorribleSubs*Ushio*Tora*720p

# All Doki BD releases
Doki*x1080*BD
```

Example of blacklist:
```
# E.g. we hate .mp4 containers
*.mp4
```

License
-------

MIT
