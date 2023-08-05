#!/usr/bin/env python3

import argparse
import logging
import os
import time

import pandas as pd
import pysam
import sqlalchemy

from cdis_pipe_utils import df_util
from cdis_pipe_utils import pipe_util
from cdis_pipe_utils import time_util


def get_record_ids_set(uuid, abam, engine, logger):
    start_time = time.time()
    logger.info('running step `get qcfail record ids` from: %s' % abam)
    id_set=set()
    samfile = pysam.AlignmentFile(abam, 'rb')
    for read in samfile.fetch():
        if (read.flag & 512) == 512: # http://samtools.github.io/hts-specs/SAMv1.pdf page 4
            id_set.add(read.qname)
    samfile.close()
    logger.info('completed step `get qcfail record ids` from: %s' % abam)
    elapsed_time = time.time() - start_time

    #store time
    df = time_util.store_seconds(uuid, elapsed_time, logger)
    table_name = 'time_remove_qcfail_get_record_ids'
    unique_key_dict = { 'uuid': uuid, 'bam_path': abam }
    df_util.save_df_to_sqlalchemy(df, unique_key_dict, table_name, engine, logger)

    #store id_set to db
    df = pd.DataFrame(data={'record_ids': sorted(list(id_set))})
    df['uuid'] = uuid
    df['bam_path'] = abam
    df.columns = ['record_ids', 'uuid', 'bam_path']
    table_name = 'remove_qcfail_get_record_ids'
    unique_key_dict = { 'uuid': uuid, 'bam_path': abam }
    df_util.save_df_to_sqlalchemy(df, unique_key_dict, table_name, engine, logger)
    return id_set


def remove_record_ids(uuid, id_set, abam, outbam_path, engine, logger):
    start_time = time.time()
    samfile_in = pysam.AlignmentFile(abam, 'rb')
    samfile_in_header = samfile_in.header
    logger.info('samfile_in_header=%s' % samfile_in_header)
    samfile_out = pysam.AlignmentFile(outbam_path, 'wb', header=samfile_in_header)
    for read in samfile_in.fetch():
        if read.qname in id_set:
            continue
        else:
            samfile_out.write(read)
    elapsed_time = time.time() - start_time

    #store time
    df = time_util.store_seconds(uuid, elapsed_time, logger)
    table_name = 'time_remove_qcfail_remove_record_ids'
    unique_key_dict = { 'uuid': uuid, 'bam_path': abam }
    df_util.save_df_to_sqlalchemy(df, unique_key_dict, table_name, engine, logger)
    return


def get_outbam_path(abam):
    template_bam = os.path.basename(abam)
    out_dir = os.path.join(os.getcwd(), 'remove_qcfail')
    os.makedirs(out_dir, exist_ok=True)
    outbam_path = os.path.join(out_dir, template_bam)
    return outbam_path


def main():
    parser = argparse.ArgumentParser('remove qc failed reads in a secondary BAM using a source/first BAM')
    parser.add_argument('-f', '--first_bam', required=True)
    parser.add_argument('-s', '--second_bam', required=True)
    parser.add_argument('-u', '--uuid', required=True)
    parser.add_argument('-d', '--debug',
        action = 'store_const',
        const = logging.DEBUG,
        dest = 'level',
        help = 'Enable debug logging.',
    )

    parser.set_defaults(level = logging.INFO)
    args = parser.parse_args()
    
    first_bam = args.first_bam
    second_bam = args.second_bam
    uuid = args.uuid
    level=args.level

    outbam_path = get_outbam_path(second_bam)

    ##logging
    logging.basicConfig(
        filename=os.path.join(uuid + '_remove_qcfail.log'),  # /host for docker
        level=args.level,
        filemode='a',
        format='%(asctime)s %(levelname)s %(message)s',
        datefmt='%Y-%m-%d_%H:%M:%S_%Z',
    )
    logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
    logger = logging.getLogger(__name__)
    hostname = os.uname()[1]

    sqlite_name = uuid + '.db'
    engine_path = 'sqlite:///' + os.path.join(sqlite_name)
    engine = sqlalchemy.create_engine(engine_path, isolation_level='SERIALIZABLE')

    outbam_name = os.path.basename(outbam_path)
    outbam_base, outbam_ext = os.path.splitext(outbam_name)
    if pipe_util.already_step(os.getcwd(), 'remove_qcfail_' + outbam_base, logger):
        logger.info('already completed step `remove qcfail` of %s' % second_bam)
    else:
        id_set = get_record_ids_set(uuid, first_bam, engine, logger)
        remove_record_ids(uuid, id_set, second_bam, outbam_path, engine, logger)
        logger.info('completed running step `remove qcfail` of %s' % second_bam)
        pipe_util.create_already_step(os.getcwd(), 'remove_qcfail_' + outbam_base, logger)
    return


if __name__ == '__main__':
    main()
