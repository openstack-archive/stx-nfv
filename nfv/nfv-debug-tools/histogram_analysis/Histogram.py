#!/usr/bin/env python
################################################################################
#
# Copyright (c) 2017 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
################################################################################
#
# Description: Un-gzips nfv-vim log files within the same directory and generates
#              CSVs based on the processes found related to histogram data,
#              naming each CSV after the process found in the log files whose
#              log data it is storing. Each CSV file contains 3 columns of
#              data: TIMESTAMP, average execution time, hits per sample
#              This script is meant to be used with the plotter.py data visualization
#              script.
#
# Behaviour   : The script runs without any input arguments, copies all nfv-vim
#               log files found, gzipped or not, and places them into a directory
#               called logs/ where it un-gzips any zipped files (this retains the
#               original gzipped files). After this it begins parsing each nfv-vim
#               log file found, starting from the highest numbered e.g. nfv-vim.log.20
#               down to the lowest nfv-vim.log.1 or nfv-vim.log. This script expects
#               the highest number of digits following .log. to be two i.e [0-9][0-9]
#               CSV files will be stored in a new directory called csv/
#               Timestamps for each sample are written to the CSV, followed by the
#               average execution time which is each execution time in the sample,
#               multiplied by its respective number of hits during that sample, and
#               then all of these values summed together, divided by the sum comprising
#               the total number of hits for that particular sample. The third column
#               is simply the total number of hits for that same (across all execution
#               times).
#
# Place this script in a directory containing the gzipped or ungzipped logs you would
# like to generate CSV files for.
#
# Run the script with ./Histogram.py
#
################################################################################

from collections import defaultdict
import glob
import os
from subprocess import call

dir = os.path.dirname(__file__)
csvDir = os.path.join(dir, 'csv/')
logDir = os.path.join(dir, 'logs/')

if not os.path.exists(csvDir):
    os.makedirs(csvDir)

if not os.path.exists(logDir):
    os.makedirs(logDir)

call("cp nfv-vim.log nfv-vim.log.[0-9] nfv-vim.log.[0-9][0-9] nfv-vim.log.[0-9].gz nfv-vim.log.[0-9][0-9].gz logs/", shell=True)
call("gunzip logs/nfv-vim.log.[0-9].gz logs/nfv-vim.log.[0-9][0-9].gz", shell=True)


class Parser(object):
    def __init__(self):
        self.proc = ""  # Name of process being read
        self.timestamp = ""  # Timestamp found on line stating process name
        self.write = False  # Flag indicating data has yet to be written
        self.stored = False  # Flag indicating that there is new data stored
        self.length = 0  # Time duration of process
        self.instanceCount = 0  # Number of hits for the particular duration
        self.rollingCount = 0  # Sum of the hits for each duration parsed within the sample
        self.total = 0  # Specific duration multiplied by number of hits for that duration
        self.avg = 0  # Average execution time of process
        self.unit = ""  # Unit execution time was recorded in
        self.csvs = defaultdict(list)  # Stores unique processes in a dict of lists

    # Resets variables when a new process begins to be read in logs
    def reset(self):
        self.length = 0
        self.avg = 0
        self.instanceCount = 0
        self.rollingCount = 0
        self.total = 0
        self.proc = ""
        self.unit = ""
        self.write = False
        self.stored = False

    # Adds log data for a process to the csvs dictionary
    def add(self, proc, total, timestamp, rollingCount):
        if rollingCount != 0:
            avg = total / float(rollingCount)
        else:
            avg = 0
        self.csvs[proc].append(timestamp + "," + str(avg) + "," + str(rollingCount) + ",")
        self.reset()

    def main(self):
        # Sorts the log files to read them in descending order
        sorted_files = glob.glob(logDir + "nfv-vim.log*")
        sorted_files.sort(reverse=True)
        for logFile in sorted_files:
            with open(logFile, "r+") as f:
                cfgLines = f.read().splitlines()
                for line in cfgLines:
                    if "Histogram" in line:
                        if self.write or self.stored:
                            self.add(self.proc,
                                     self.total,
                                     self.timestamp,
                                     self.rollingCount)
                        self.write = True
                        self.proc = line.partition("Histogram: ")[2]
                        self.proc = ("".join(self.proc.split())).rstrip(':')
                        self.timestamp = line.split()[0]
                    elif "histogram.py" in line:
                        line = line.split()
                        self.length = int(line[8])
                        self.unit = line[9]
                        self.instanceCount = int(line[10])
                        if "decisecond" in self.unit:
                            self.length *= 100
                        elif "secs" in self.unit:
                            self.length *= 1000
                        self.total = self.total + self.instanceCount * self.length
                        self.rollingCount += self.instanceCount
                        self.stored = True
            f.close()
            if self.write or self.stored:
                self.add(self.proc, self.total, self.timestamp, self.rollingCount)

        for process in self.csvs:
            with open(os.path.join(csvDir, process + ".csv"), 'w+') as csvOut:
                for line in self.csvs[process]:
                    csvOut.write(line + "\n")
            csvOut.close()


process = Parser()
process.main()
print("\nComplete\n")
