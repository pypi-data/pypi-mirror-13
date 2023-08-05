#!/usr/bin/env python

import argparse
import logging
import sys

from cdis_pipe_utils import pipe_util

import tools.bam_stats as bam_stats
import tools.picard_buildbamindex as picard_buildbamindex
import tools.picard_markduplicates as picard_markduplicates
import tools.picard_validatesamfile as picard_validatesamfile
from tools.picard_calculatehsmetrics_tcga import picard_calculatehsmetrics as picard_calculatehsmetrics_tcga
from tools.picard_collecthsmetrics_target import picard_collecthsmetrics as picard_collectwgsmetrics_target

def main():
    parser = argparse.ArgumentParser('picard docker tool')

    # Logging flags.
    parser.add_argument('-d', '--debug',
        action = 'store_const',
        const = logging.DEBUG,
        dest = 'level',
        help = 'Enable debug logging.',
    )
    parser.set_defaults(level = logging.INFO)
    
    # Required flags.
    parser.add_argument('--tool_name',
                        required = True,
                        help = 'picard tool'
    )
    parser.add_argument('--uuid',
                        required = True,
                        help = 'uuid string',
    )
    
    # Tool flags
    parser.add_argument('--bam_path',
                        required = False
    )
    parser.add_argument('--reference_fasta_path',
                        required = False
    )
    parser.add_argument('--bait_intervals_path',
                        required = False
    )
    parser.add_argument('--target_intervals_path',
                        required = False
    )

    # setup required parameters
    args = parser.parse_args()
    tool_name = args.tool_name
    uuid = args.uuid

    logger = pipe_util.setup_logging(tool_name, args, uuid)
    engine = pipe_util.setup_db(uuid)

    be_lenient = True
    if tool_name == 'BuildBamIndex':
        bam_path = pipe_util.get_param(args, 'bam_path')
        picard_buildbamindex.picard_buildbamindex(uuid, bam_path, engine, logger, be_lenient)
    elif tool_name == 'CollectAlignmentSummaryMetrics':
        bam_path = pipe_util.get_param(args, 'bam_path')
        reference_fasta_path = pipe_util.get_param(args, 'reference_fasta_path')
        bam_stats.do_picard_metrics(uuid, bam_path, reference_fasta_path, scratch_dir, engine, logger, 'CollectAlignmentSummaryMetrics')
    elif tool_name == 'CollectMultipleMetrics':
        bam_path = pipe_util.get_param(args, 'bam_path')
        reference_fasta_path = pipe_util.get_param(args, 'reference_fasta_path')
        bam_stats.do_picard_metrics(uuid, bam_path, reference_fasta_path, engine, logger, 'CollectMultipleMetrics')
    elif tool_name == 'MarkDuplicates':
        bam_path = pipe_util.get_param(args, 'bam_path')
        picard_markduplicates.bam_markduplicates(uuid, bam_path, engine, logger, be_lenient)
    elif tool_name == 'MarkDuplicatesWithMateCigar':
        bam_path = pipe_util.get_param(args, 'bam_path')
        picard_markduplicates.bam_markduplicateswithmatecigar(uuid, bam_path, engine, logger, be_lenient)
    elif tool_name == 'ValidateSamFile':
        bam_path = pipe_util.get_param(args, 'bam_path')
        picard_validatesamfile.picard_validatesamfile(uuid, bam_path, engine, logger)
    elif tool_name == 'CollectWgsMetrics':
        bam_path = pipe_util.get_param(args, 'bam_path')
        reference_fasta_path = pipe_util.get_param(args, 'reference_fasta_path')
        picard_collectwgsmetrics(uuid, bam_path, reference_fasta_path, engine, logger)
    elif tool_name == 'CalculateHsMetrics_tcga':
        bam_path = pipe_util.get_param(args, 'bam_path')
        reference_fasta_path = pipe_util.get_param(args, 'reference_fasta_path')
        json_path = pipe_util.get_param(args, 'json_path')
        interval_dir = pipe_util.get_param(args, 'interval_dir')
        wxs_dict['bait_intervals_path'] = bait_intervals_path
        wxs_dict['target_intervals_path'] = target_intervals_path
        picard_calculatehsmetrics_tcga(uuid, bam_path, json_path, interval_dir, engine, logger, wxs_dict = wxs_dict)
    elif tool_name == 'CalculateHsMetrics_target':
        bam_path = pipe_util.get_param(args, 'bam_path')
        reference_fasta_path = pipe_util.get_param(args, 'reference_fasta_path')
        json_path = pipe_util.get_param(args, 'json_path')
        interval_dir = pipe_util.get_param(args, 'interval_dir')
        wxs_dict['bait_intervals_path'] = bait_intervals_path
        wxs_dict['target_intervals_path'] = target_intervals_path
        picard_calculatehsmetrics_target(uuid, bam_path, json_path, interval_dir, engine, logger, wxs_dict = wxs_dict)
    else:
        sys.exit('No recognized tool was selected')
        
    return


if __name__ == '__main__':
    main()
