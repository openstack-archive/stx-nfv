#!/usr/bin/env python
################################################################################
#
# Copyright (c) 2017 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
################################################################################
#
# Description: Graphs nfv-vim histogram data from CSV files to html page and saves
#              saves it locally.
#
# Behaviour   : The script takes in arguments from the command line such as specific
#               process names, or the name of a grouping of processes, and graphs
#               them in a local html file using plotly. The x-axis displays
#               datestamps corresponding to when the sample in the csv file was taken,
#               and the y-axis displays either the average execution time of the
#               processes during each sample, or the difference in total hits that
#               process experienced from one sample period to the previous sample
#               period. Both average execution times and the delta hit count can
#               be displayed on the same graph using two y-axes. The CSV files must
#               be generated prior to running this script by running Histogram.sh.
#               A config called logplot.cfg will be generated the first time this
#               script is run and will automatically populate itself with all processes
#               listed in the csv/ directory. Change the N to a Y in the right column
#               of the config file to have that process graphed when running this script
#               via config settings. Groupings of processes can also be made under the
#               groups section by following the same N/Y format as above. When a group
#               name is specified all processes listed under that group name will be
#               graphed if they have a Y in their right-column.
#
# To run this script ensure that plotly is installed.
# To do this enter: sudo pip install plotly
#
#
# If no arguments are entered when running this script it will default to running
# the proceses in logplot.cfg with a Y in their rightmost column, and will display
# the average execution time on the y-axis for all available samples.
#
################################################################################

import os
import csv
import sys
import time
import plotly
import plotly.graph_objs as go
from plotly.graph_objs import Scatter, Layout
from plotly import tools
from glob import iglob
import subprocess
from builtins import input

dir = os.path.dirname(__file__)
fig = plotly.graph_objs.graph_objs.Figure
pth = os.path.join(dir, 'csv/')

execTime = False # Indicates if average execution time is to be graphed or not
default = False # Indicates no commands were entered and to run with default settings (run config with -t option)
oneAxis = False # Causes the generated graph to have two y-axes sharing an x-axis with both avg execution time and hits being graphed
config = False # Indicates whether to pull process names from logplot.cfg or not
hits = False # Indicates if the delta of hits between samples is to be graphed
markers = False
lines = False
timestamp = []
dateRange = []
warnings = []
procs = []
group = []
graphName = ""
plotType = ""


def helpMessage():
    print("\n" + "-" * 120)
    print("NFV-VIM Histogram Graphing Script\n")
    print("This script is meant to graph average execution times and the delta of hits between sample periods for processes in nfv-vim logs.\n")
    print("Usage:\n")
    print(" -c                ... runs from the logplot.cfg (c)onfig file. All processes in the first list with a Y\n"
          "                       in the far-right column will be included in the generated graph.\n")
    print(" -d                ... command used to specify a (d)ate range within which you would like to see log data.\n"
          "                       The format is YYYY/MM/DD-YYYY/MM/DD with the lower bound on the left, and the upper\n"
          "                       bound on the right. The range is up to and including the bounds. To have a bound simply\n"
          "                       cover all datestamps before or after a bound, omit the undefined bound. Only one bound can be\n"
          "                       unspecified in this way.\n"
          "                       e.g. -d 2016/12/01-2016/12/12\n"
          "                            -d -2016/12/12   To use all logs prior to and including 2016/12/12\n"
          "                            -d 2016/12/01-   To use all logs after and including 2016/12/01\n")
    print(" -t                ... used to indicate that you would like the graph to display average execution (t)imes\n"
          "                       along the y-axis.\n")
    print(" -h                ... used to indicate that you would like the graph to display the dela of (h)its between\n"
          "                       sample periods on the y-axis.\n")
    print(" -l                ... used to set the graph to be a line graph. (Can be used with -m as well)\n")
    print(" -m                ... used to set the graph to be a scatterplot. (Can be used with -l as well)\n")
    print(" -lm               ... used to set the graph to be a scatterplot with connecting lines. This same effect can also be\n"
          "                       achieved by using -l -m\n")
    print(" -n                ... used to (n)ame the file that will be generated by this script. Files can be found in the\n"
          "                       Graphs/ directory, found inside the directory containing this script. Do not include spaces in\n"
          "                       the file name. If no name is specified, the name will default to the timestamp from when the\n"
          "                       script was run.\n"
          "                       e.g. 01-24-2017.html\n")
    print(" -oneaxis          ... used to generate a graph with two Y-axes sharing an x-axis. Average execution time's y-axis is\n"
          "                       on the right, and delta Hits per sample's y-axis is on the left. Used to look for correlations. The \n"
          "                       name of the process being graphed will have _time or _hits appended to it so you can tell which\n"
          "                       y-axis to relate it to. Only works if both -h and -t flags are used. Can be used for multiple processes.\n"
          "                       e.g. -h -t -oneaxis --p process1 process2\n")
    print(" --g               ... will run the script for processes specified in logplot.cfg under the (G)roups heading.\n"
          "                       All processes listed under the named group's heading will be included in the graph.\n"
          "                       Space-delimit the groups to be included. This must be the last command entered.\n"
          "                       e.g. --g group1 group2\n")
    print(" --p               ... follow this with a space-delimited list of (p)rocesses you would like to graph together.\n"
          "                       This must be the last command entered.\n")
    print(" --update          ... This will update the master list of process at the beginning of the logplot.cfg file:\n"
          "                       Processes not currently listed in the master list will be added and their run status set to N.\n\n")
    print("Note: If neither the -t nor -h tag is used, the script will default to display the average execution time on the y-axis.\n\n")
    print("Examples:\n")
    print("./plotter.py -c -d 2016/12/3-2016/12/10 -t -n ConfigOutput_Dec_3-10          ... This will graph all processes with a Y in their\n"
          "                                                                                 right-most column in the config file, using logs\n"
          "                                                                                 with a timestamp between Dec 3rd and 10th 2016,\n"
          "                                                                                 and will display their average execution time in\n"
          "                                                                                 the y-axis. The file will be called\n"
          "                                                                                 ConfigOutput_Dec_3-10.html")
    print("./plotter.py -h -t --g group1                                                ... This will generate two graphs, one with the delta of hits\n"
          "                                                                                 on the y-axis, and the other with the average execution time\n"
          "                                                                                 in the y-axis, for processes listed under group1 in\n"
          "                                                                                 logplot.cfg.\n"
          "                                                                                 period will be displayed on the y-axis.\n")
    print("./plotter.py                                                                 ... This will run the default settings, which are to run\n"
          "                                                                                 for the processes enabled in the master list in\n"
          "                                                                                 the config file, to use log information for all dates\n"
          "                                                                                 available, to show average execution time on the y-axis,\n"
          "                                                                                 and to name the file with the current day's datestamp.")
    print("-" * 120)


# Appends new processes found via CSV filenames to the master process list in logplot.cfg if there are not already present.
# If logplot.cfg has not been generated yet, this will create it and add process names found in filenames in ./csv
def updater(configExists=True):
    procs = []
    existingProcs = []
    newProcs = []
    position = 0 # Tracks position of the end of the master process list so new processes can be added above it.

    os.chdir(pth)
    for name in iglob("*.csv"):
        procs.append(str(name)[:-4])
    os.chdir("..")
    if not configExists:
        f = open(os.path.join(dir, 'logplot.cfg'), "w")
        for p in procs:
            f.write(p + " " * (59 - len(p)) + "N\n")
        f.write("#" * 20 + "END OF PROCESS LIST" + "#" * 21 + "\n\n")
        f.write("#" * 27 + "GROUPS" + "#" * 27 + "\n")
        f.write("#GroupSTART\n")
        f.write("GroupName=ExampleGroupName1\n")
        f.write("ExampleProcessName1" + " " * 40 + "N\n")
        f.write("ExampleProcessName2" + " " * 40 + "N\n")
        f.write("#GroupEND\n")
        f.write("-" * 60 + "\n")
        f.write("GroupName=ExampleGroupName2\n")
        f.write("ExampleProcessName3" + " " * 40 + "N\n")
        f.write("ExampleProcessName4" + " " * 40 + "N\n")
        f.write("#GroupEND\n")
        f.write("#" * 20 + "END OF GROUPS" + "#" * 27)
        f.close()
    else:
        with open(os.path.join(dir, 'logplot.cfg'), "r+") as f:
            cfgLines = f.read().splitlines()
            for cfgProc in cfgLines:
                if "#END" in cfgProc:
                    break
                existingProcs.append(cfgProc.split()[0])
                position += 1
            for p in procs:
                if p not in existingProcs:
                    newProcs.append(p + " " * (59 - len(p)) + "N")
            procs = cfgLines[:position] + newProcs + cfgLines[position:]
            f.seek(0)
            f.write("\n".join(procs))
            f.truncate()
            f.close()


# Appends process names found in the specified group to the list of processes to be graphed.
def gCommand(groups):
    procs = []
    f = open(os.path.join(dir, 'logplot.cfg'), "r")
    cfgLines = f.read().splitlines()

    for g in groups:
        groupFound = False
        finishedGroup = False

        for i in range(len(cfgLines)):
            liNum = i
            if str("GroupName=" + g) == cfgLines[i].strip():
                groupFound = True
                while not finishedGroup:
                    liNum += 1
                    if "GroupEND" in cfgLines[liNum]:
                        finishedGroup = True
                    else:
                        cfgLine = cfgLines[liNum].split()
                        if cfgLine[1] == "Y":
                            procs.append(cfgLine[0])
                else:
                    break
        else:
            if not groupFound:
                warnings.append("WARNING: The following group could not be found: %s\n\t\t Please check your logplot.cfg file for the intended group name." % (g,))

    f.close()
    return procs


# Appends processes explicitly named by the user to the list of processes to be run.
# If the process name specified using the --p command does not match the name of any processes taken from .csv filenames, the user is given
# a list of known processes containing the name they entered. If they enter one of the provided names, it will be added to the list. If the
# user enters "s", the process in question will be skipped and the script will continue. If they user enters "q" the script will exit.
def pCommand(pList):
    procList = []
    for i in range(len(pList)):
        csvFile = str(pList[i]) + ".csv"
        procName = str(pList[i])
        isFile = False

        if os.path.isfile(os.path.join(pth, csvFile)):
            isFile = True
            procList.append(pList[i])
        else:
            while(not isFile):
                print("\nFiles containing keyword: %s" % (str(procName)))
                csvFile = str(procName) + ".csv"
                for root, directories, filenames in os.walk(pth):
                    for filename in filenames:
                        if procName.lower() in filename.lower():
                            if (str(procName) + ".csv") == str(filename):
                                isFile = True
                                procList.append(str(procName).strip())
                                break
                            else:
                                print(" " + filename[:-4])
                    else:
                        procName = str(input("\nEnter the corrected process name, q to quit, or s to skip: ")).strip()
                    if procName == "s":
                        isFile = True
                        break
                    elif procName == "q":
                        sys.exit()
    return procList


# Stores the average execution time, or delta hit count data into into a plotly graph obj, and restricts sample to be within a certain
# date range if specified. If plots is 1, one graph will be generated. If plots is 2, two graphs will be generated with one above the other.
def storeGraphData(procs, dateRange=[], execTime=False, hits=False, plots=1):
    graphData = {}
    prevHitTotal = 0
    timeList = [[] for p in range(len(procs))]
    dateList = [[] for p in range(len(procs))]
    hitList = [[] for p in range(len(procs))]
    if dateRange:
        for i in range(len(procs)):
            csvFile = str(procs[i]) + ".csv"
            with open(os.path.join(pth, csvFile), 'rb') as f:
                reader = csv.reader(f, delimiter=',', quoting=csv.QUOTE_NONE)
                for ts, at, h, n in reader:
                    t = ts.split("T")
                    date = ''.join(x for x in t[0].split('-'))
                    if (int(date) >= int(dateRange[0])) and (int(date) <= int(dateRange[1])):
                        timeList[i].append(at)
                        dateList[i].append(str(ts[0:10:1] + " " + ts[11:]))
                        hitList[i].append(int(h) - prevHitTotal)
                        prevHitTotal = int(h)
            f.close()
            hitList[i][0] = None
            graphData['trace' + str(i)] = go.Scatter(x=dateList[i],
                                                     y=timeList[i] if execTime else hitList[i],
                                                     mode=plotType,
                                                     name=(procs[i] if not oneAxis else (procs[i] + "_" + ("time" if execTime else "hits"))))
            if plots == 1:
                fig.append_trace(graphData['trace' + str(i)], 1, 1)
            elif plots == 2:
                fig.append_trace(graphData['trace' + str(i)], 2, 1)

    else:
        for i in range(len(procs)):
            csvFile = str(procs[i]) + ".csv"
            with open(os.path.join(pth, csvFile), 'rb') as f:
                reader = csv.reader(f, delimiter=',', quoting=csv.QUOTE_NONE)
                for ts, at, h, n in reader:
                    timeList[i].append(at)
                    dateList[i].append(str(ts[0:10:1] + " " + ts[11:]))
                    hitList[i].append(int(h) - prevHitTotal)
                    prevHitTotal = int(h)
            f.close()
            hitList[i][0] = None
            graphData['trace' + str(i)] = go.Scatter(x=dateList[i],
                                                     y=timeList[i] if execTime else hitList[i],
                                                     mode=plotType,
                                                     name=(procs[i] if not oneAxis else (procs[i] + "_" + ("time" if execTime else "hits"))))
            if plots == 1:
                fig.append_trace(graphData['trace' + str(i)], 1, 1)
            elif plots == 2:
                fig.append_trace(graphData['trace' + str(i)], 2, 1)


# Formats the graph by adding axis titles, changing font sizes, setting there to be two separate graphs or two graphs sharing an x-axis etc.
def formatGraph(two, oneAxis):
    fig['layout'].update(showlegend=True)
    if two:
        if oneAxis:
            fig['layout']['xaxis1'].update(title='Timestamp', titlefont=dict(size=20, color='#4d4d4d'))
            fig['layout']['yaxis1'].update(title='Hits Per Sample', titlefont=dict(size=20, color='#4d4d4d'))
            fig['layout']['yaxis2'].update(title='Average Execution Time (milliseconds)', anchor='x', overlaying='y', side='right', position=1, titlefont=dict(size=20, color='#4d4d4d'))
        else:
            fig['layout']['xaxis1'].update(title='Timestamp', titlefont=dict(size=20, color='#4d4d4d'))
            fig['layout']['yaxis1'].update(title='Average Execution Time (milliseconds)', titlefont=dict(size=20, color='#4d4d4d'))
            fig['layout']['xaxis2'].update(title='Timestamp', titlefont=dict(size=20, color='#4d4d4d'))
            fig['layout']['yaxis2'].update(title='Hits Per Sample', titlefont=dict(size=20, color='#4d4d4d'))
        fig['layout'].update(title=graphName, titlefont=dict(size=26))
    else:
        fig['layout'].update(
            title=graphName,
            xaxis=dict(
                title="Timestamp",
                titlefont=dict(
                    family='Courier New, monospace',
                    size=18,
                    color='#4d4d4d'
                )
            ),
            yaxis=dict(
                title="Average Execution Time (milliseconds)" if execTime else "Hits Per Sample",
                titlefont=dict(
                    family='Courier New, monospace',
                    size=18,
                    color='#4d4d4d'
                )
            )
        )


# Sets the name of the saved html file.
def setFilename(graphName):
    validName = False
    if not os.path.exists("Graphs/"):
        os.makedirs("Graphs/")
    os.chdir(os.path.join(dir, 'Graphs/'))
    if not graphName:
            graphName = time.strftime("%m-%d-%Y")
    if os.path.exists(str(graphName + ".html")):
        n = 1
        while(not validName):
            if os.path.exists(str(graphName + "(" + str(n) + ").html")):
                n += 1
            else:
                graphName = graphName + "(" + str(n) + ")"
                validName = True
    return graphName


print("Welcome to plotter, type --help for information")
# Checks that plotly is installed, otherwise graphs cannot be generated.
plotCheck = subprocess.getstatusoutput("pip list | grep plotly")
if plotCheck[0] == 0:
    if "plotly" not in plotCheck[1]:
        print("\n\tWARNING: Plotly is not installed on your system.\n\tPlease install it with: sudo pip install plotly\n")
        sys.exit()
# Checks to see if logplot.cfg already exists, creates it if not.
if not os.path.isfile(os.path.join(dir, 'logplot.cfg')):
    print("Generating logplot.cfg")
    updater(False)
    print("logplot.cfg created.")
if not os.path.isdir('./csv'):
    print("\n\tWARNING: ./csv directory is missing. Please run Histogram.sh or make sure directory has not been renamed.\n")
    sys.exit()

command = sys.argv # Takes arguments from the command line

if len(command) == 1:
    print("Running with default settings.")
    default = True
else:
    for i in range(1, len(command)):
        if command[i] == "-c": # Use config file
            config = True
        elif command[i] == "--g": # Groups
            for j in range(i + 1, len(command)):
                group.append(command[j])
            procs = gCommand(group)
            break
        elif command[i] == "-t": # Average execution time
            execTime = True
        elif command[i] == "-h": # Delta hits between samples
            hits = True
        elif command[i] == "-l": # Graph with lines
            lines = True
        elif command[i] == "-m": # Graph with markers (scatter)
            markers = True
        elif command[i] == "-lm": # Graph with lines and markers
            lines = True
            markers = True
        elif command[i] == "-d": # Date range
            dateRange = command[i + 1].split('-')
            if dateRange[0]:
                lower = dateRange[0].split("/")
                dateRange[0] = lower[0] + lower[1].zfill(2) + lower[2].zfill(2)
            else:
                dateRange[0] = "0" * 8
            if dateRange[1]:
                upper = dateRange[1].split("/")
                dateRange[1] = upper[0] + upper[1].zfill(2) + upper[2].zfill(2)
            else:
                dateRange[1] = "9" * 8
            i += 1
        elif command[i] == "-n": # Name of file to be generated
            graphName = command[i + 1]
            i += 1
        elif command[i] == "-oneaxis": # Have hit and time data displayed on same graph
            oneAxis = True
        elif (command[i] == "--help") or (command[i] == "--h"): # Print help message and exit script
            helpMessage()
            sys.exit()
        elif command[i] == "--p": # User-specified processes
            for j in range(i + 1, len(command)):
                procs.append(command[j])
            procs = pCommand(procs)
            break
        elif command[i] == "--update":
            print("Updating...")
            updater()
            print("Update complete.")
            sys.exit()

# If neither average execution time nor delta hit count are specified to be shown, default to showing average execution time.
if (not execTime) and (not hits):
    execTime = True

# Default settings can be changed as desired.
if default:
    config = True
    execTime = True

if (lines and markers):
    plotType = "lines+markers"
elif lines:
    plotType = "lines"
else:
    plotType = "markers"

if config:
    f = open(os.path.join(dir, 'logplot.cfg'), "r")
    procList = f.read().splitlines()
    for p in procList:
        if "#END" in p:
            break
        cfgLine = p.split()
        if cfgLine[1] == "Y":
            csvFile = cfgLine[0] + ".csv"
            if os.path.exists(os.path.join(pth, csvFile)):
                procs.append(cfgLine[0])
            else:
                warnings.append("WARNING: %s does not exist." % (csvFile,))
    f.close()

# If both average execution time and delta hits are specified to be shown, generate two graphs if -oneaxis wasn't specified.
# If only one of execution time and delta hits was specified, generate one graph.
if procs:
    if (execTime and hits):
        if(not oneAxis):
            fig = tools.make_subplots(rows=2, cols=1)
            storeGraphData(procs, dateRange, execTime, False, 1)
            storeGraphData(procs, dateRange, False, hits, 2)
        else:
            fig = tools.make_subplots(rows=1, cols=1)
            storeGraphData(procs, dateRange, False, hits, 1)
            storeGraphData(procs, dateRange, execTime, False, 1)
    else:
        fig = tools.make_subplots(rows=1, cols=1)
        storeGraphData(procs, dateRange, execTime, hits)

    formatGraph((execTime and hits), oneAxis)

    # Generates the plot
    plotly.offline.plot(fig, filename=setFilename(graphName) + ".html")
else:
    warnings.append("NO GRAPH GENERATED BECAUSE NO VALID GROUP OR PROCESS NAME SPECIFIED.")

# If any warnings occured, print them
if warnings:
    print("\n\t" + ("\n\t").join(warnings) + "\n")
