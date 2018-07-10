#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from nfv_common import debug

from . import _parsers

DLOG = debug.debug_get_logger('forensic-evidence')


def evidence_from_files(files, start_date, end_date, progress=None):
    """
    Gather evidence
    """
    records = list()
    file_ctrl = dict()

    total_lines = 0
    for parser_name, file_name in files.items():
        total_lines += sum(1 for _ in open(file_name))
        file_ctrl[file_name] = (parser_name, open(file_name), None)

    lines_read = 0
    while 0 < len(file_ctrl):
        # Read a record from each file.
        for file_name, (parser_name, f, record) in file_ctrl.items():
            if record is None:
                line = f.readline()
                while line:
                    parser = _parsers.parser_get(parser_name)
                    record = parser.parse(start_date, end_date, line)
                    if record is not None:
                        file_ctrl[file_name] = (parser_name, f, record)
                        break
                    line = f.readline()
                    lines_read += 1

        # Remove files that do not have any more records.
        for file_name, (parser_name, f, record) in file_ctrl.items():
            if record is None:
                del file_ctrl[file_name]

        # Sort records and take the earliest record.
        earliest = None
        for file_name, (parser_name, f, record) in file_ctrl.items():
            if earliest is None:
                earliest = (file_name, parser_name, f, record)
            else:
                _, _, _, earliest_record = earliest
                if earliest_record['timestamp'] > record['timestamp']:
                    earliest = (file_name, parser_name, f, record)

        if earliest is not None:
            file_name, parser_name, f, record = earliest
            file_ctrl[file_name] = (parser_name, f, None)
            records.append(record)

        if progress is not None:
            progress((float(lines_read) / total_lines) * 100)

    return records
