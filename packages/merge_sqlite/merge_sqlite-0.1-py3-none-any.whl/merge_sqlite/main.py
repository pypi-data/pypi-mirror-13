#!/usr/bin/env python3

import argparse
import os
import subprocess
import sys

def do_shell_command(cmd, stdout=subprocess.STDOUT, stderr=subprocess.PIPE):
    try:
        output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True)
    except Exception as e:
        sys.exit('failed cmd: %s' % str(cmd))
    return output


def main():
    parser = argparse.ArgumentParser('merge an arbitrary number of sqlite files')
    parser.add_argument('-s', '--source_sqlite', action='append', required=True)
    parser.add_argument('-u', '--uuid', required=True)
    args = parser.parse_args()

    source_sqlite_list = args.source_sqlite
    uuid = args.uuid

    destination_sqlite_path = uuid+'.db'
    print('destination_sqlite_path=%s' % destination_sqlite_path)
    for source_sqlite_path in source_sqlite_list:
        ('source_sqlite_path=%s' % source_sqlite_path)
        source_sqlite_name = os.path.splitext(os.path.basename(source_sqlite_path))[0]
        source_dump_path = source_sqlite_name + '.sql'
        #dump
        cmd = ['sqlite3', source_sqlite_path, "\'.dump\'", '>', source_dump_path ]
        shell_cmd = ' '.join(cmd)
        do_shell_command(shell_cmd)
        #load
        cmd = ['sqlite3', destination_sqlite_path, '<', source_dump_path]
        shell_cmd = ' '.join(cmd)
        do_shell_command(shell_cmd)
                                        
if __name__ == '__main__':
    main()
