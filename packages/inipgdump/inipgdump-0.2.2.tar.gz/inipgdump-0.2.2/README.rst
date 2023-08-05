inipgdump
=========

It works on python2.6 and python2.7
-----------------------------------

Installation:

::

    pip install inipgdump

Creates a dump of the PostgreSQL database. The naming format of dump:

::

    $host_$dbname_$datetime.dump

Stores the specified number of dumps, deletes the old dumps.

Options to create a dump taken from the configuration file in the
following format:

::

    [database]
    DATABASE_NAME = your_value
    DATABASE_USER = your_value
    DATABASE_PASSWORD = your_value
    DATABASE_HOST = your_value
    DATABASE_PORT = your value

Usage:

::

    (without rotation): inipgdump config_file.ini /dump/dir
    (with rotation): inipgdump config_file.ini /dump/dir keep_count
              

Examples of usage in the cron::

::

    # Daily backup
    0 4 2-31 * 0-5 inipgdump /path/to/config_file.ini /dumps/daily 7
    # Weekly backup
    0 4 2-31 * 6 inipgdump /path/to/config_file.ini /dumps/weekly 8
    # Monthly backup
    0 4 1 2-12 * inipgdump /path/to/config_file.ini /dumps/monthly 12
    # Yearly backup
    0 4 1 1 * inipgdump /path/to/config_file.ini /dumps/yearly 10

