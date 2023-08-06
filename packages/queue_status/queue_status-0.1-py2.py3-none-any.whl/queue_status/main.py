#!/usr/bin/env python

import argparse
import configparser
import logging
import os
import time

import pandas as pd

from cdis_pipe_utils import df_util
from cdis_pipe_utils import pipe_util
from cdis_pipe_utils import time_util
from cdis_pipe_utils import postgres

def get_db_cred(db_cred_s3url, s3cfg_path, logger):
    cmd = ['s3cmd', '-c', s3cfg_path, 'get', db_cred_s3url]
    output = pipe_util.do_command(cmd, logger)
    db_cred_path = os.path.basename(db_cred_s3url)
    return db_cred_path

def get_connect_dict(db_cred_s3url, s3cfg_path, logger):
    db_cred_path = get_db_cred(db_cred_s3url, s3cfg_path)
    config = configparser.ConfigParser()
    config.read(db_cred_path)
    connect_dict = dict(config['DEFAULT'])
    os.remove(db_cred_path)
    return connect_dict
    

def main():
    parser = argparse.ArgumentParser('update status of job')
    # Logging flags.
    parser.add_argument('-d', '--debug',
        action = 'store_const',
        const = logging.DEBUG,
        dest = 'level',
        help = 'Enable debug logging.',
    )
    parser.set_defaults(level = logging.INFO)

    parser.add_argument('--db_cred_s3url',
                        required = True
    )
    parser.add_argument('--repo',
                        required = True
    )
    parser.add_argument('--repo_hash',
                        required = True
    )
    parser.add_argument('--s3cfg_path',
                        required = True
    )
    parser.add_argument('--status',
                        required = True
    )
    parser.add_argument('--table_name',
                        required=True
    )
    parser.add_argument('--uuid',
                        required=True
    )
    args = parser.parse_args()

    db_cred_s3url = args.db_cred_s3url
    repo = args.repo
    repo_hash = args.repo_hash
    s3cfg_path = args.s3cfg_path
    status = args.status
    table_name = args.table_name
    uuid = args.uuid

    tool_name = 'queue_status'
    
    logger = pipe_util.setup_logging(tool_name, args, uuid)

    conn_dict = get_connect_dict(db_cred_s3url, s3cfg_path, logger)

    engine = postgres.db_connnect(conn_dict)

    time_seconds = time.time()
    datetime_now = str(datetime.datetime.now())

    status_dict = dict()
    status_dict['time_seconds'] = time_seconds
    status_dict['datetime_now'] = datetime_now
    status_dict['uuid'] = [uuid]
    status_dict['repo'] = repo
    status_dict['repo_hash'] = repo_hash
    status_dict['status'] = status
    df = pd.DataFrame(status_dict)
    
    unique_key_dict = {'uuid': uuid, 'repo_hash': repo_hash, 'status': status }
    df_util.save_df_to_sqlalchemy(df, unique_key_dict, table_name, engine, logger)

    return
