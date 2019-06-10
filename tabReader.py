"""
This file parses the input file, loads the data into objects of the following types, and then uses their fields/methods to output an HTML file that holds sheet music.
created from the stored data and using the StaffString class from the display utility library. There are no new types defined in this file, however, this is the
file that runs the overall program.

Compatibility Note: This file is what makes this project not incompatible with Python 2. Since Python 3 strings are represented in Unicode, the string.translate() method was changed. This method now requires a single argument, a translation table, which is different from the string.translate() method in Python 2.
While string.strip() seems to work for the purposes of these methods, it appears to be much slower than string.translate() as each combination of the passed arguments is run through and stripped.

author: Chami Lamelas
date: Summer 2019
"""

from exceptionsLibrary import TabException, TabFileException, MeasureException, TabConfigurationException, LoggingException, TabIOException
from typeLibrary import Song, Measure, Slice
from configUtils import ConfigReader
from logging import Logger
from sys import argv
import time

"""
Returns whether a line with the following 3 properties is a timing line:

(i) It contains at least 1 non-whitespace character
(ii) It has been stripped on the end of whitespace
(iii) It has had all its tabs replaced with spaces

Lines that are meant to list the timings of notes that are played must be made up of ONLY the following characters and must contain at least 1 non-whitespace character.

newline/carriage return: "\n" (at the end)
tab: "\t" (cleaned by string.expandtabs() in loadLinesIntoLists())
tie marking: "+"
dot marking: "."
space: " "
*only* the uppercase letters that denote lengths of time: W, H, Q, E, and S

params:
line - a line who satisfies (i)-(iii) that will be checked to see if it satisfies the above property
"""
def checkNoteLine(line):
    return len(line.translate({ord(c) : None for c in "+. WHQES"})) == 0

"""
Returns whether a line with the following 2 properties represents a string line:

(i) It has at least 1 non-whitespace character
(ii) It has been stripped on the end of whitespace

Lines that are meant to be strings must:

(a) The first non-whitespace character must be G, D, A, or E followed by a "|" or just be "|"
(b) Following either case of (i), a sequence of only the following characters:

vertical bar: "|"
hyphen: "-"
digits (0-9)

(c) The last non-whitespace character must be a "|"
(d) Be at least 4 characters long, not counting the whitespace at either end.

params:
line - a line who satisfies (i) and (ii) that will be checked if it satisfies (a)-(d)
legend - set of characters that are allowed in strings
"""
def checkStringLine(line, legend):
    line = line.lstrip() # strip any whitespace before checking props. (a)-(d)
    if len(line) < 4:
        return False
    checkSet = set("|-0123456789").union(legend)
    return ((line[0] in "GDAE" and line[1] == "|") or line.startswith("|")) and len(line[1:].translate({ord(c) : None for c in checkSet})) == 0 and line.endswith("|")

"""
Parses a given note. Here a note is not in the string-fret representation referenced in the type library classes, but at an index (or 2) in a string array. This
method places this note into a Slice which wraps the conversion procedure (see its doc. in typeLibrary.py).

params:
string - an array representing a guitar string
idx - position of 1st digit of the fret on the strings
slice - Slice to add the note to
stringID - character ID of the guitar string

Returns whether or not to skip the next index. This occurs in the case of 2-digit frets where both string[i] and string[i + 1] must be considered to determine the
note properly.

Raises TabFileException if slice.addNote() fails.
"""
def parseNote(string, idx, slice, stringID):
    skip = False
    fret = string[idx]
    if fret.isdigit():
        if idx < len(string) - 1 and string[idx + 1].isdigit(): # found a 2-digit fret number, update fret variable
            fret += string[idx + 1]
            skip = True # skip reading the next index in the string as its fret value is considered as part of this note
        slice.addNote(stringID, fret)
    return skip

"""
Updates a Song object given a subset of the input data stored as a group of lists.

params:
song - a Song object to be updated
start - starting index of new data to be loaded into 'song' (*)
end - ending index of new data to be loaded into 'song' (*)
notes - list of timing info.
gString - representation of G-string
dString - representation of D-string
aString - representation of A-string
eString - representation of E-string
lastSlice - last Slice to be added to 'song'

pre-conditions:
if notes is not empty, it should have the same length as the string lists (gString, dString, aString, and eString)
(*) start and end must be valid indices in the above lists

Returns the last Slice to be added to 'song', replaces param. 'lastSlice'

Raises TabConfigurationException if the Slice class' mapping from timing symbols to timing lengths was not loaded.
Raises TabFileException if helper method parseNote() fails, Slice.setLength() fails, or an improper measure line was detected. For the former 2, see their docs.
Raises TabException if Slice.applyDot() or Slice.tie() fail (see their doc.)
Raises MeasureException if Song.addMeasure() fails (see its doc.)
"""
def updateSong(song, start, end, notes, gString, dString, aString, eString, lastSlice):
    measure = Measure()
    i = start
    while i <= end:
        slice = Slice()
        skip1 = False

        if parseNote(gString, i, slice, "G"):
            skip1 = True
        if parseNote(dString, i, slice, "D"):
            skip1 = True
        if parseNote(aString, i, slice, "A"):
            skip1 = True
        if parseNote(eString, i, slice, "E"):
            skip1 = True

        if slice.isEmpty():
            if gString[i] == "|" or dString[i] == "|" or aString == "|" or eString[i] == "|":
                if gString[i] != "|" or dString[i] != "|" or aString[i] != "|" or eString[i] != "|":
                    raise TabFileException("improper measure line detected", "Not all string arrays have a \"|\" at column " + str(i), line=i)
                if not measure.isEmpty():
                    song.addMeasure(measure)
                    measure = Measure()
                # else don't add empty Measures to the Song
            # else all the strings at this index don't matter: members of legend or are "-"
        else:
            if notes:
                slice.setLength(notes[i])
                if i > 0 and notes[i - 1] == "+":
                    lastSlice.tie(slice)
                j = i+1
                while j < len(notes) and notes[j] == ".":
                    slice.applyDot()
                    j = j + 1
            # else timing hasn't been loaded, do nothing
            measure.addSlice(slice) # regardless, add the Slice to the temp. measure
            lastSlice = slice # update last Slice for future ties

        if skip1:
            i += 2
        else:
            i += 1
    return lastSlice

"""
Builds a Song given the list of lines read from the input file and configuration data loaded by the method run(). At the end of
this method, if it completes successfully, the data from the input tab file will have been parsed and stored appropriately in
Song, Measure, and Slice objects.

params:
lines - list of lines read from input file
song - Song object that will be loaded with Measures and Slices
hasTiming - config option that specifies whether user has provided timing info.
tabSpacing - number of spaces in a tab in user's text editor (see README)
legend - list of other chars. that will appear in string lines (see README)
loadedLines - array used to report info. on progress of parsing 'lines'
    loadedLines[0] - number of lines read
    loadedLines[1] - number of lines interpreted as string/timing lines

Raises TabFileException if any of the following occur:
    - lengths of strings and timing lines are unequal
    - the method did not interpret a valid number of string/timing lines
Furthermore, in the event of helper method updateSong() failing, the following exceptions could be raised:
    - TabFileException
    - TabException
    - MeasureException
    - TabConfigurationException
The reasons as to why these exceptions could be raised seemed to lengthy to add here. Instead, look at that method's doc.
"""
def buildSong(lines, song, hasTiming, tabSpacing, legend, loadedLines):
    notes = list()
    gString = list()
    dString = list()
    aString = list()
    eString = list()

    lastSlice = Slice()
    nextUpdate = 0
    while loadedLines[0] < len(lines):
        sLine = lines[loadedLines[0]].rstrip()
        if len(sLine) == 0: # whitespace line
            loadedLines[0] += 1
            if (hasTiming and loadedLines[1] % 5 == 0) or (not hasTiming and loadedLines[1] % 4 == 0):
                song.placeExtraLine(" ")
            # else: this is an empty line in between strings, ignore it
            continue

        if hasTiming:
            if loadedLines[1] % 5 == 0:
                sLine = sLine.expandtabs(tabSpacing)
                arr = list(sLine)
                if not song.hasExtraText or checkNoteLine(sLine):
                    nextUpdate = len(notes)
                    notes.extend(arr)
                    loadedLines[1] += 1
                else:
                    song.placeExtraLine(sLine)
            else:
                arr = list(sLine)
                if not song.hasExtraText or checkStringLine(sLine, legend):
                    if loadedLines[1] % 5 == 1:
                        gString.extend(arr)
                        for i in range(len(notes), len(gString)):
                            notes.append(" ")
                    elif loadedLines[1] % 5 == 2:
                        dString.extend(arr)
                    elif loadedLines[1] % 5 == 3:
                        aString.extend(arr)
                    elif loadedLines[1] % 5 == 4:
                        eString.extend(arr)
                        if len(gString) != len(dString) or len(gString) != len(aString) or len (gString) != len(eString) or len(gString) != len(notes):
                            raise TabFileException("arrays not loaded properly", "The arrays holding strings (lengths = {0}, {1}, {2}, {3}) and the array holding the timing ({4}) must have the same length.".format(len(gString), len(dString), len(aString), len(eString), len(notes)), line=loadedLines[0])
                        lastSlice = updateSong(song, nextUpdate, len(gString)-1, notes, gString, dString, aString, eString, lastSlice)
                    loadedLines[1] += 1
                else:
                    song.placeExtraLine(sLine)
        else:
            arr = list(sLine)
            if not song.hasExtraText or checkStringLine(sLine, legend):
                if loadedLines[1] % 4 == 0:
                    nextUpdate = len(gString)
                    gString.extend(arr)
                elif loadedLines[1] % 4 == 1:
                    dString.extend(arr)
                elif loadedLines[1] % 4 == 2:
                    aString.extend(arr)
                elif loadedLines[1] % 4 == 3:
                    eString.extend(arr)
                    if len(gString) != len(dString) or len(gString) != len(aString) or len(gString) != len(eString):
                        raise TabFileException("arrays not loaded properly", "The arrays holding strings (lengths = {0}, {1}, {2}, {3}) must have the same length.".format(len(gString), len(dString), len(aString), len(eString)), line=loadedLines[0])
                    lastSlice = updateSong(song, nextUpdate, len(gString)-1, notes, gString, dString, aString, eString, lastSlice)
                loadedLines[1] += 1
            else:
                song.placeExtraLine(sLine)
        loadedLines[0] += 1

    if (hasTiming and loadedLines[1] % 5 != 0) or (not hasTiming and loadedLines[1] % 4 != 0): # if timing was supplied, count should be a multiple of 5 and if not it should be a multiple of 4
        errorMsg = ""
        if hasTiming:
            errorMsg = "The number of lines interpreted as strings and timing identifiers ({0}) is incorrect, should be a multiple of 5".format(count)
        else:
            errorMsg = "The number of lines interpreted as strings ({0}) is incorrect, should be a multiple of 4".format(count)
        raise TabFileException("input file line count incorrect", errorMsg)

"""
Reads the input tab file and loads it into its initial representation as 5 arrays (4 for the guitar strings, 1 for the timing symbols), builds the Song using the
above method, and then creates the output HTML file.

params:
logger - Logger object to report output

Raises a LoggingException if any of the logging operations used below fail
"""
def run(logger):
    try:
        if len(argv) < 2: # input tab file was not specified
            raise TabException("No input file can be found.")

        inFilename = argv[1]
        logger.log("Successfully located input file \"{0}\". Beginning tab-reading program configuration...".format(inFilename))
        start = time.time()

        rdr = ConfigReader()
        if rdr.readConfigFile(): # prepare config. file by loading it into a ConfigReader. If config file could not be loaded, reader reports it built & read the default config. file
            logger.log("Configuration file was loaded successfully. Beginning tab-reading program...")
        else:
            logger.log(msg="Configuration file was not found. Default configuration file was created and loaded instead.", type=Logger.WARNING)

        hasTiming = rdr.getTiming()
        tabSpacing = rdr.getTabSpacing()
        legend = rdr.getLegend()
        Slice.loadMaps()

        notes = list()
        gString = list()
        dString = list()
        aString = list()
        eString = list()

        try: # try to load list of strings from tab input file and raise a more appropriate exception than IOError to the user if one occurs
            with open(inFilename) as inputFile:
                lines = inputFile.readlines()
            logger.log("Input tab file \"{0}\" was opened and closed successfully.".format(inFilename))
        except IOError as i:
            raise TabIOException("opening tab file", str(i))

        song = Song(rdr.getGapsize(), rdr.getHasExtra())
        loadedLines = [0, 0]
        buildSong(lines, song, hasTiming, tabSpacing, legend, loadedLines)
        logger.log("Song building of the data from \"{0}\" finished without any parsing errors. {1} out of the {2} loaded lines were read successfully.".format(inFilename, loadedLines[0], len(lines)))
        logStr = ""
        logType = Logger.INFO
        if loadedLines[1] > 0:
            logStr += "{0} out of the {1} read lines were interpreted as string lines"
        else:
            logType = Logger.WARNING
            logStr += "No lines were interpreted as string lines"
        if hasTiming:
            logStr += " and timing lines"
        logger.log(type=logType, msg=logStr.format(loadedLines[1], loadedLines[0]) + "; if this is not the expected count, please check your input file and the configuration file.")

        pathNoExt = argv[1][:-4] # get file path without 4-character extension & use it to create output filename
        outFilename = pathNoExt+"_staff.html"
        try: # try to write Song output to HTML file and raise a more appropriate exception than IOError to the user if one occurs
            with open(outFilename, "w+", encoding="utf-8") as outFile:
                outFile.write("<!DOCTYPE HTML><html><title>" + pathNoExt[pathNoExt.rfind("\\")+1:]+" staff </title><body><pre>" + str(song) + "</pre></body></html>")
            logger.log("Output HTML file \"{0}\" was opened and {1} Measures created from input tab file {2} were written successfully before closing.".format(outFilename, song.numMeasures(), inFilename))
        except IOError as i:
            raise TabIOException("creating HTML file", str(i))
        logger.log("Program completed successfully in {0} seconds.".format(round(time.time()-start, 6)))

    except TabFileException as t:
        logger.log(msg=str(t), type=Logger.ERROR)
    except TabConfigurationException as c:
        logger.log(msg=str(c), type=Logger.ERROR)
    except TabIOException as i:
        logger.log(msg=str(i), type=Logger.ERROR)
    except TabException as e:
        logger.log(msg=str(e), type=Logger.ERROR)

"""
Script that runs program. The 2nd program argument (this file's name is the 1st one) must be the input tab's file name.
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
