#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
import os
import re
import yaml
import datetime

from pyparsing import Word, Combine, Suppress, Literal, Regex
from pyparsing import nums, alphas


class NfvVimParser(object):
    """
    NFV-VIM Parser
    """
    def __init__(self, config_data):
        self._config_data = config_data

        year = Word(nums)
        month = Suppress('-') + Word(nums)
        day = Suppress('-') + Word(nums)

        hour = Suppress('T') + Word(nums)
        minute = Suppress(':') + Word(nums)
        second = Suppress(':') + Word(nums)
        millisecond = Suppress('.') + Word(nums)

        hostname = Word(alphas + nums + '_' + '-' + '.')

        pid = (Suppress(Word(alphas + '_' + alphas + '-' + '[')) + Word(nums) +
               Suppress(']'))

        ignore = Suppress(Word(alphas))

        filename = Combine(Word(alphas + '_') + Literal(".py"))

        lineno = Suppress('.') + Word(nums)

        message = Regex(".*")

        self.__pattern = (year + month + day + hour + minute + second +
                          millisecond + hostname + pid + ignore + filename +
                          lineno + message)

    def parse_message(self, filename, lineno, message):
        for log in self._config_data['logs']:
            if log.get('file', None) is not None:
                if filename != log['file']:
                    continue

            if log.get('lineno', None) is not None:
                if lineno != str(log['lineno']):
                    continue

            query_obj = re.match(log['regex'], message)
            if query_obj is not None:
                message_data = dict()
                message_data['type'] = log['type']
                message_data['log'] = message
                for idx, field_name in enumerate(log['fields'], 1):
                    message_data[field_name] = query_obj.group(idx)
                return message_data
        return None

    def parse(self, start_date, end_date, line):
        record = None

        try:
            # verify minimum line length is met
            if 70 < len(line):
                parsed = self.__pattern.parseString(line)

                timestamp = datetime.datetime(int(parsed[0]), int(parsed[1]),
                                              int(parsed[2]), int(parsed[3]),
                                              int(parsed[4]), int(parsed[5]),
                                              int(parsed[6]) * 1000)

                if start_date <= timestamp <= end_date:
                    message_data = self.parse_message(parsed[9], parsed[10],
                                                      parsed[11])
                    if message_data is not None:
                        record = dict()
                        record['timestamp'] = timestamp
                        record['hostname'] = parsed[7]
                        record['pid'] = parsed[8]
                        record['filename'] = parsed[9]
                        record['lineno'] = parsed[10]
                        record['data'] = message_data

        except Exception as e:
            print("Bad line: %s, exception=%s." % (line, e))

        return record


def parser_initialize():
    """
    Initialize module
    """
    path = os.path.abspath(__file__)
    config_file = os.path.dirname(path) + "/config/nfv-vim.yaml"
    if os.path.isfile(config_file):
        config_data = yaml.load(open(config_file))
        return NfvVimParser(config_data)
    return None


def parser_finalize():
    """
    Finalize module
    """
    pass
