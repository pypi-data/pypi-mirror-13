This is a really simple Python parser for the `journald binary export format <http://www.freedesktop.org/wiki/Software/systemd/export/>`_.

It can parse journal entries from a file-like object or an iterable, and yields each entry as a dict containing all attributes of the journal entry::

    from __future__ import print_function  # if using Python 2.x

    from journalparse import journalparse


    with open("some_file", "rb") as fp:
        for entry in journalparse(fp):
            print(entry)

    # ... or ...

    data = b"_MESSAGE=blah"
    for entry in journalparse(data):
        print(entry)

There are no requirements other than Python. Tested on Python 3.5 but should work on Python 2.6+ and 3.2+.


