"""
This file parses the input file, loads the data into objects of the following types, and then uses their fields/methods to output an HTML file that holds sheet music.
created from the stored data and using the StaffString class from the display utility library. There are no new types defined in this file, however, this is the
file that runs the overall program.

Compatibility Note: The definition of checkStringLine() and checkNoteLine() below are what makes this program not compatible with Python 2.x. Since Python 3 strings are represented in Unicode,
the string.translate() method was changed. This method now requires a single argument, a translation table, which is different from the string.translate() method in Python 2.

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
This method parses the read data from the tab file (stored in a set of arrays) and loads it into a provided Song object by parsing the parameter data and appropriately
creating Slices and Measures to place into the Song.

params:
song - a Song to be built
notes - an array that holds the symbols denoting the length of time of each Slice in the tab (could be empty if no timing is provided)
gString - array holding notes to be played on the 4th (or g) string of the bass
dString - array holding notes to be played on the 3rd (or d) string of the bass
aString - array holding notes to be played on the 2nd (or a) string of the bass
eString - array holding notes to be played on the 1st (or e) string of the bass

pre-condition: all arrays are of the same length unless notes is empty.

Raises MeasureException if song.addMeasure() fails
Raises TabFileException if parseNote() fails or if an improper measure line is detected.
Raises TabException if Slice.setLength() or Slice.applyDot() fails
To see better explanations, view these methods' doc.
"""
def buildSong(song, notes, gString, dString, aString, eString):
    measure = Measure() # temporary Measure variable that allows 1 Measure at a time to be built, added to the Song, and then reset
    lastSlice = Slice() # to track ties, this variable keeps track of the last Slice that was added to the Song (either in the current Measure or the prev. one)
    i = 0
    while i < len(gString): # allowed since all arrays are of the same length, i can iterate through them
        slice = Slice()  # temporary Slice to add Notes too from arrays
        skip1 = False # based on parseNote outputs, skip reading the next index

        # parses each Note at index i in each array and puts it into the Slice
        if parseNote(gString, i, slice, "G"):
            skip1 = True
        if parseNote(dString, i, slice, "D"):
            skip1 = True
        if parseNote(aString, i, slice, "A"):
            skip1 = True
        if parseNote(eString, i, slice, "E"):
            skip1 = True

        if slice.isEmpty(): # if Slice was empty, check that index i in the string arrays hold a measure line. If the line is valid, add temp. Measure var. to the Song and reset it
            if gString[i] == "|":
                if dString[i] != "|" or aString[i] != "|" or eString[i] != "|":
                    raise TabFileException("improper measure line detected", "Not all string arrays have a \"|\" at column " + str(i))
                elif not measure.isEmpty():
                    song.addMeasure(measure)
                    measure = Measure()
            # else all the strings at index i had all "-"; do nothing
        else: # if user specified that the timing wasn't supplied, the notes array was never filled
            if notes: # if timing was supplied, set the Slice's length to its raw time at notes[i] and tie it if notes[i-1]="+" and apply any dots that follow notes[i]
                slice.setLength(notes[i])
                if i > 0 and notes[i - 1] == "+":
                    lastSlice.tie(slice)
                j = i+1
                while j < len(notes) and notes[j] == ".":
                    slice.applyDot()
                    j = j + 1
            measure.addSlice(slice) # regardless, add the Slice to the temp. measure
            lastSlice = slice # update last Slice for future ties
        if skip1: # iterate i appropriately to account for 2-digit frets
            i = i + 2
        else:
            i = i + 1

"""
Returns whether a line that has been stripped on the ends of whitespace is a line representing the note timings.

lines that are meant to list the timings of notes that are played must be made up of ONLY the following characters.

newline/carriage return: "\n"
tab: "\t"
tie marking: "+"
dot marking: "."
space: " "
*only* the uppercase letters that belong to the timing ids {W, H, Q, E, S}
"""
def checkNoteLine(line):
    if len(line) == 0:
        return False
    return len(line.translate({ord(c) : None for c in "\t+. WHQES"})) == 0

"""
Returns whether a line that has been stripped on the ends of whitespace is a line representing a string.

lines that are meant to be strings must start with G, D, A, or E, followed by a "|", followed by a sequence of only the following characters, end with a "|", and must be at least 4 characters long.

newline/carriage return: "\n"
tab: ""\t"
vertical bar: "|"
hyphen: "-"
space: " "
digits (0-9)
"""
def checkStringLine(line):
    if len(line) < 4:
        return False
    return line[0] in "GDAE" and line[1] == "|" and len(line[1:].translate({ord(c) : None for c in "\t|-()0123456789 "})) == 0 and line.endswith("|")

"""
Takes a String list of the lines of the input file and loads the input into 4 (or 5) arrays. This will be the first representation of the notes in the song, where each string of
the bass is an array. Furthermore, if the timing is supplied, the 5th array holds the timings of the of each note represented as letters (W, H, Q, etc.). In the end, each array
should have the same length if the input tab file is indeed valid. As a result, spaces are placed into the notes list to stretch it to correspond to the g-string.

params:
lines - list of Strings from the input file
notes - holds the timings' ids
gString - array representing g-string
dString - array representing d-string
aString - array representing a-string
eString - array representing e-string
hasTiming - truth value of timing being supplied (taken from config file)

Raises TabFileException if the number of lines interpreted as either timing information and strings is incorrect. To see how lines are interpreted see the docs. for the 2 methods
above.
"""
def loadLinesIntoLists(lines, notes, gString, dString, aString, eString, hasTiming):
    count = 0 # count of lines that are either string lines or timing lines
    lastNoteExt = 0 # length of prev. timing line. This will be extended as explained in the method doc.
    for line in lines:
        sLine = line.strip()
        arr = list(sLine) # array rep. of file line stripped of carriage return
        if hasTiming: # if user has specified that timing was supplied -> read lines in groups of 5, and note lines must be checked for
            if count % 5 == 0: # if any multiple of 5 lines has been read, the next line should be a note line if input file is valid.
                if checkNoteLine(sLine): # check that its a valid note-timing line, if so add it to the notes array and mark how long it is for future extension and count it
                    notes.extend(arr)
                    count += 1
                    lastNoteExt = len(arr)
                # else, skip this line
            else: # other lines will be string lines
                if checkStringLine(sLine): # check that its a valid string line, if so add it to the appropriate string array and count it
                    if count % 5 == 1: # 1 line after a multiple of 5 is a g-string
                        gString.extend(arr)
                        # need to update the last addition to the notes list to add spaces to make the timing line of the input file have the same length as the g-string below it
                        # otherwise, for input files where tabs may be on separate lines, the notes' timings would not be above the 1st digit of the fret of the note corresponding
                        # to it. This is what is needed in buildSong in order to properly parse the input data and load it into a Song object.
                        for i in range(lastNoteExt, len(arr)):
                            notes.append(" ")
                    elif count % 5 == 2: # 2 lines after a multiple of 5 is a d-string
                        dString.extend(arr)
                    elif count % 5 == 3: # 3 lines after a multiple of 5 is an a-string
                        aString.extend(arr)
                    elif count % 5 == 4: # 4 lines after a multiple of 5 is an e-string
                        eString.extend(arr)
                    count += 1
                # else, skip the line
        else: # the user has specified that no timing was supplied -> read lines in groups of 4
            if checkStringLine(sLine): # check that this is a valid string line, if so add it to the appropriate string array and count it
                if count % 4 == 0: # if any multiple of 4 lines has been read, the next line should be a g-string
                    gString.extend(arr)
                elif count % 4 == 1: # 1 line after a multiple of 4 is a d-string
                    dString.extend(arr)
                elif count % 4 == 2: # 2 lines after a multiple of 4 is an a-string
                    aString.extend(arr)
                elif count % 4 == 3: # 3 lines after a multiple of 4 is an e-string
                    eString.extend(arr)
                count += 1
            # else, skip the line
    if (hasTiming and count % 5 != 0) or (hasTiming and count % 4 != 0): # if timing was supplied, count should be a multiple of 5 and if not it should be a multiple of 4
        errorMsg = ""
        if hasTiming:
            errorMsg = "The number of lines interpreted as strings and timing identifiers {0} is incorrect, should be a multiple of 5".format(count)
        else:
            errorMsg = "The number of lines interpreted as strings {0} is incorrect, should be a multiple of 4".format(count)
        raise TabFileException("input file line count incorrect", errorMsg)
    if len(gString) != len(dString) or len(gString) != len(aString) or len (gString) != len(eString) or (len(notes) > 0 and len(gString) != len(notes)): # loaded arrays must have the same length for further parsing
        errorMsg = ""
        if len(notes) > 0:
            errorMsg = "The arrays holding strings (lengths = {0}, {1}, {2}, {3}) and the array holding the timing ({4}) must have the same length.".format(len(gString), len(dString), len(aString), len(eString), len(notes))
        else:
            errorMsg = "The arrays holding strings (lengths = {0}, {1}, {2}, {3}) must have the same length.".format(len(gString), len(dString), len(aString), len(eString))
        raise TabFileException("arrays not loaded properly", errorMsg)

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
        logger.log("Successfully located input file {0}. Beginning tab-reading program...".format(inFilename))
        start = time.time()

        rdr = ConfigReader()
        if rdr.readConfigFile(): # prepare config. file by loading it into a ConfigReader. If config file could not be loaded, reader reports it built & read the default config. file
            logger.log("Configuration file was loaded successfully.")
        else:
            logger.log(msg="Configuration file was not found. Default configuration file was created and read instead.", type=Logger.WARNING)

        hasTiming = rdr.getTiming()
        Slice.loadMaps()
        notes = list()
        gString = list()
        dString = list()
        aString = list()
        eString = list()

        try: # try to load list of strings from tab input file and raise a more appropriate exception than IOError to the user if one occurs
            with open(inFilename) as inputFile:
                lines = inputFile.readlines()
            logger.log("Input tab file {0} was opened and closed successfully.".format(inFilename))
        except IOError as i:
            raise TabIOException("opening tab file", str(i))

        loadLinesIntoLists(lines, notes, gString, dString, aString, eString, hasTiming)
        logger.log("Data in input tab file {0} was loaded successfully into array representation. ".format(inFilename))
        song = Song(rdr.getGapsize())
        buildSong(song, notes, gString, dString, aString, eString)
        logger.log("Data in input tab file {0} was parsed and loaded into a Song successfully. ".format(inFilename))

        pathNoExt = argv[1][:-4] # get file path without 4-character extension & use it to create output filename
        outFilename = pathNoExt+"_staff.html"
        try: # try to write Song output to HTML file and raise a more appropriate exception than IOError to the user if one occurs
            with open(outFilename, "w+", encoding="utf-8") as outFile:
                outFile.write("<!DOCTYPE HTML><html><title>" + pathNoExt[pathNoExt.rfind("\\")+1:]+" staff </title><body><pre>" + str(song) + "</pre></body></html>")
            logger.log("Output HTML file {0} was opened and data in Song created from input tab file {1} was written successfully before closing.".format(outFilename, inFilename))
        except IOError as i:
            raise TabIOException("creating HTML file", str(i))
        logger.log("Program completed successfully in {0} seconds.".format(round(time.time()-start, 4)))

    except TabFileException as t:
        logger.log(msg=str(t), type=Logger.ERROR)
    except TabConfigurationException as c:
        logger.log(msg=str(c), type=Logger.ERROR)
    except TabIOException as i:
        logger.log(msg=str(i), type=Logger.ERROR)
    except TabException as e:
        logger.log(msg=str(e), type=Logger.ERROR)

"""
Script that runs program. The 2nd program argument (this file is the 1st one) must be the input tab's file name.
"""
try:
    logger = Logger()
    logger.open()
    run(logger)
except LoggingException as l:
    print(l)
except Exception as e:
    logger.log(msg="An unexpected error occurred: " + str(e), type=Logger.ERROR) #
finally:
    logger.close()
