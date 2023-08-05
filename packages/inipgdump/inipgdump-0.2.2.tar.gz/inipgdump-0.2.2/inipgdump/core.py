#!/usr/bin/env python

# Timur Isanov tisanov@yahoo.com

# Creates a dump of the PostgreSQL database.
# Options to create a dump taken from the configuration file in the following format:
# [database]
# DATABASE_NAME = your_value
# DATABASE_USER = your_value
# DATABASE_PASSWORD = your_value
# DATABASE_HOST = your_value
# DATABASE_PORT = your value

# Stores the specified number of dumps, deletes the old dumps.
# Examples of usage in the cron:
# Daily backup
# 0 4 2-31 * 0-5 inipgdump /path/to/config_file.ini /dumps/daily 7
# Weekly backup
# 0 4 2-31 * 6 inipgdump /path/to/config_file.ini /dumps/weekly 8
# Monthly backup
#0 4 1 2-12 * inipgdump /path/to/config_file.ini /dumps/monthly 12
# Yearly backup
# 0 4 1 1 * inipgdump /path/to/config_file.ini /dumps/yearly 10

from __future__ import print_function
from operator import itemgetter
import os
import datetime
import sys
import subprocess
import ConfigParser

def rotate(dump_dir, host, name, keep_count=30):
    dumps = []
    for l in os.listdir(dump_dir):
        if os.path.isfile(dump_dir + '/' + l):
            if host + '_' + name in l:
                if '.dump' in l:
                    dumps.append(dump_dir + '/' + l)
    dumps_with_time = {}
    for d in dumps:
        dumps_with_time[d] = datetime.datetime.fromtimestamp(os.path.getmtime(d))
    sorted_dumps_by_time = sorted(dumps_with_time.items(), key=itemgetter(1), reverse=True)
    count = 0
    for d in sorted_dumps_by_time:
        count += 1
        if count > keep_count:
            os.remove(d[0])
            print('File %s deleted by rotation' % d[0])


def make_dump(conf_file, dump_dir, keep_count):
    config = ConfigParser.ConfigParser()
    config.readfp(open(conf_file))
    host = config.get('database', 'database_host')
    name = config.get('database', 'database_name')
    user = config.get('database', 'database_user')
    password = config.get('database', 'database_password')
    port = config.get('database', 'database_port')
    if not port:
        port = '5432'
    dump_name = dump_dir + '/'+ host + '_' + name + '_' + datetime.datetime.now().strftime("%F_%H-%M") + '.dump'
    get_dump = subprocess.call("pg_dump -h %s -p %s -U %s -Fc -v --blobs %s --file %s" %
                               (host, port, user, name, dump_name),
                                env={"PGPASSWORD": password},
                                shell=True)
    if get_dump == 0:
        if keep_count > 0:
            rotate(dump_dir, host, name, keep_count)
    else:
        print('Dump creation error!')
        sys.exit(1)


def main():
    if len(sys.argv) == 3:
        keep_count = 0
    elif len(sys.argv) == 4:
        keep_count = int(sys.argv[3])
    else:
        print('Usage (without rotation): inipgdump config_file.ini /dump/dir')
        print('Usage (with rotation): inipgdump config_file.ini /dump/dir keep_count')
        sys.exit(1)
    conf_file = sys.argv[1]
    if sys.argv[2][-1] == '/':
        dump_dir = sys.argv[2][:-1]
    else:
        dump_dir = sys.argv[2]
    if not os.path.isfile(conf_file):
        print('File \'%s\' not found' % conf_file)
        sys.exit(1)
    if not os.path.isdir(dump_dir):
        print('Folder \'%s\' not found' % dump_dir)
        sys.exit(1)
    if keep_count < 0:
        print('keep_count must be greater than 0')
        sys.exit(1)
    make_dump(conf_file, dump_dir, keep_count)


if __name__ == "__main__":
    main()