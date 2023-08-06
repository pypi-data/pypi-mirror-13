maxmind-updater
===============

This is a simple library to keep a maxmind database file up to date. You can either call the ``maxmindupdater.update_db``
function in a python script, or the ``maxmind-updater`` command from a shell. Both forms take three arguments:

1. The path to the maxmind database (``.mmdb``) file to keep updated.
   The file will either be created or replaced if it is out of date.
2. Your maxmind account license key.
3. The database edition ID, e.g. ``GeoIP2-Country``.

The library can be installed using ``pip install maxmindupdater``.

In addition to the main database file which is placed at the path specified, the script will also keep the full ``.tar.gz``
archive downloaded from the maxmind website.
