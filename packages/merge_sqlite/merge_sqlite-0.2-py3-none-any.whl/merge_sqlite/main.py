#!/usr/bin/env python3

import argparse

import os

from cdis_pipe_utils import df_util
from cdis_pipe_utils import pipe_util
from cdis_pipe_utils import time_util

def main():
    parser = argparse.ArgumentParser('merge an arbitrary number of sqlite files')
    parser.add_argument('-s', '--source_sqlite', action='append', required=True)
    parser.add_argument('-u', '--uuid', required=True)
    args = parser.parse_args()

    source_sqlite_list = args.source_sqlite
    uuid = args.uuid

    tool_name = 'merge_sqlite'
    logger = pipe_util.setup_logging(tool_name, args, uuid)
    engine = pipe_util.setup_db(uuid+'_log')

    step_dir = os.getcwd()
    if pipe_util.already_step(step_dir, uuid + '_db', logger):
        logger.info('already completed step `merge_sqlite`')
    else:
        logger.info('running step `merge_sqlite`')
        for source_sqlite_path in source_sqlite_list:
            ('source_sqlite_path=%s' % source_sqlite_path)
            source_sqlite_name = os.path.splitext(os.path.basename(source_sqlite_path))[0]

            #dump
            source_dump_path = source_sqlite_name + '.sql'
            cmd = ['sqlite3', source_sqlite_path, "\'.dump\'", '>', source_dump_path ]
            shell_cmd = ' '.join(cmd)
            pipe_util.do_shell_command(shell_cmd, logger)

            #load
            destination_sqlite_path = uuid + '.db'
            cmd = ['sqlite3', destination_sqlite_path, '<', source_dump_path]
            shell_cmd = ' '.join(cmd)
            pipe_util.do_shell_command(shell_cmd, logger)
        pipe_util.create_already_step(step_dir, uuid + '_db', logger)
    return

if __name__ == '__main__':
    main()
