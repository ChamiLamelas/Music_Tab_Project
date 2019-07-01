"""
This file runs the tab reading program, that is:

(1) Reads the configuration file. (see configUtils.py)
(2) Parses the input tab file into music type objects. (see parsingUtils.py, typeLibrary.py)
(3) Takes the data from the type objects and displays it in an HTML file in sheet music representation. (see displayUtils.py)
(4) Reports program status (including timing) and any errors in a LOG file. (see loggingUtils.py, exceptionsLibrary.py)

author: Chami Lamelas
date: Summer 2019
"""

import sys

if sys.version_info < (3, 4):
    sys.exit("Python version too old (must be at least 3.4).")
# otherwise, continue with program.

from loggingUtils import Logger
from exceptionsLibrary import TabException, TabFileException, MeasureException, TabConfigurationException, TabIOException, LoggingException
from typeLibrary import Song
from configUtils import ConfigReader, ConfigOptionID
from parsingUtils import buildSong
import time

"""
Reads the input tab file and loads into a Song object using helper 'buildSong()'

params:
logger - Logger object to report output

Raises a LoggingException if any of the logging operations used below fail
"""
def run(logger):
    try:
        if len(sys.argv) < 2: # input tab file must be the 2nd prog. arg.
            raise TabException("No input file can be found.")

        inFilename = sys.argv[1]
        logger.log("Successfully located input file \"{0}\" in program arguments. Beginning tab-reading program configuration...".format(inFilename))

        rdr = ConfigReader()
        if rdr.open(): # prepare config. file by loading it into a ConfigReader.
            logger.log("Configuration file was found and loaded successfully.")
        else:
            logger.log(msg="Configuration file was not found. Default configuration file was created and loaded instead.", type=Logger.WARNING)

        rdr.readTiming()
        rdr.readGapsize()
        rdr.readTabSpacing()
        rdr.readPlayingLegend()
        rdr.readHasExtra()
        rdr.readKeepExtra()
        timingSupplied = rdr.getSettingForOption(ConfigOptionID.TIMING_SUPPLIED)
        Song.loadPlayingLegend(rdr.getSettingForOption(ConfigOptionID.PLAYING_LEGEND))

        if timingSupplied:
            rdr.readTimingSymbolsList()
            Song.loadTimingDataFromSymbolList(rdr.getSettingForOption(ConfigOptionID.TIMING_SYMBOLS))
        # else: no point in reading these options, they aren't needed

        song = Song(rdr.getSettingForOption(ConfigOptionID.GAPSIZE))
        loadedLines = [0, 0] # used in error reporting & is updated by 'parsingUtils.buildSong()'

        logger.log("The contents of the configuration file were read successfully. Beginning tab-reading...")

        try: # try to load list of strings from tab input file and raise a more appropriate exception than IOError to the user if one occurs
            with open(inFilename) as inputFile:
                lines = inputFile.readlines()
            logger.log("Input tab file \"{0}\" was opened and closed successfully.".format(inFilename))
        except IOError as i:
            raise TabIOException("opening tab file", str(i))

        start = time.time()
        buildSong(lines, song, rdr, loadedLines)

        # log a more detailed report of the result of Song building based on the data in 'loadedLines'
        logger.log("Song building of the data from \"{0}\" finished without any parsing errors. {1} out of the {2} loaded line(s) were read successfully.".format(inFilename, loadedLines[0], len(lines)))
        logStr = ""
        logType = Logger.INFO
        if loadedLines[1] > 0:
            logStr += "{0} out of the {1} read line(s) were interpreted as string line(s)".format(loadedLines[1], loadedLines[0])
        else:
            logType = Logger.WARNING
            logStr += "No lines were interpreted as string lines"
        if timingSupplied:
            logStr += " and timing lines"
        logger.log(type=logType, msg=logStr + ". {0} Measure object(s) were created.".format(song.numMeasures()))

        pathNoExt = inFilename[:-4] # get file path without 4-character extension & use it to create output filename
        outFilename = pathNoExt+"_staff.html"
        try: # try to write Song output to HTML file and raise a more appropriate exception than IOError to the user if one occurs
            with open(outFilename, "w+", encoding="utf-8") as outFile:
                outFile.write("<!DOCTYPE HTML><html><title>" + pathNoExt[pathNoExt.rfind("\\")+1:]+" staff </title><body><pre>" + str(song) + "</pre></body></html>")
            logger.log("Output HTML file \"{0}\" was opened and Song data was written successfully before closing.".format(outFilename, song.numMeasures(), inFilename))
        except IOError as i:
            raise TabIOException("creating HTML file", str(i))
        logger.log("Tab-reading and sheet music generation was completed successfully in {0} second(s).".format(round(time.time()-start, 6)))

    except TabException as e:
        logger.log(msg=str(e), type=Logger.ERROR)

"""
Script that runs the program. The 2nd program argument (this file's name is the 1st one) must be the input tab's file name.
"""
try:
    logger = Logger()
    logger.open()
    run(logger)
except LoggingException as l:
    print(l)
except Exception as e:
    logger.log(msg="An unexpected error occurred: " + str(e), type=Logger.ERROR)
finally:
    logger.close()
