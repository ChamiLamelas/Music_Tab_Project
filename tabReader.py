"""
This file parses the input file, loads the data into objects of the following types, and then uses their fields/methods to output an HTML file that holds tablature
created from the stored data and using the StaffString class from the display utility library. There are no new types defined in this file, however, this is the
file that runs the overall program.

author: Chami Lamelas
date: Summer 2019
"""

from exceptionsLibrary import TabException, TabFileException, MeasureException, TabConfigurationException, LoggingException
from typeLibrary import Song, Measure, Slice
from configUtils import ConfigReader
from logging import Logger
from sys import argv

# TODO things to add: different guitar tunings; ability to read files that don't have quarter note, eigth note, etc. specified; have a guitar version?

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

Raises TabException if slice.addNote() fails.
"""
def parseNote(string, idx, slice, stringID):
    skip = False
    fret = string[idx]
    if fret.isdigit():
        if idx < len(string) - 1 and string[idx + 1].isdigit(): # found a 2-digit fret number
            fret += string[idx + 1]
            skip = True
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

Raises MeasureException if song.addMeasure() fails, TabException if parseNote(), Slice.setLength(), Slice.applyDot() fail, or if an improper measure line is detected.
To see better explanations, view these method's doc.
"""
def buildSong(song, notes, gString, dString, aString, eString):
    measure = Measure()
    lastSlice = Slice()
    i = 0
    while i < len(gString):
        #print(notes[i],gString[i],dString[i],aString[i],eString[i],len(song.measures))
        slice = Slice()
        skip1 = False
        try:
            if parseNote(gString, i, slice, "G"):
                skip1 = True
            if parseNote(dString, i, slice, "D"):
                skip1 = True
            if parseNote(aString, i, slice, "A"):
                skip1 = True
            if parseNote(eString, i, slice, "E"):
                skip1 = True
        except ValueError: # thrown by addNote
            raise TabException("Frets must be valid integers. {0} is not a valid fret.".format(fret))

        if slice.isEmpty():
            if gString[i] == "|":
                if dString[i] != "|" or aString[i] != "|" or eString[i] != "|":
                    raise TabException("Improper measure line detected. Please review input file.")
                elif not measure.isEmpty():
                    song.addMeasure(measure)
                    measure = Measure()
            # else all the strings at index i had all "-"; do nothing
        else:
            if notes:
                slice.setLength(notes[i])
                if i > 0 and notes[i - 1] == "+":
                    lastSlice.tie(slice)
                j = i+1
                while j < len(notes) and notes[j] == ".":
                    slice.applyDot()
                    j = j + 1
            measure.addSlice(slice)
            lastSlice = slice
        if skip1:
            i = i + 2
        else:
            i = i + 1

"""
Returns whether a line that has been stripped of "\n" is a line representing the note timings.

lines that are meant to list the timings of notes that are played must be made up of ONLY the following characters:

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
    return len(line.strip("\t+. "+"".join([key for key in Slice.lengths]))) == 0

"""
Returns whether a line that has been stripped of "\n" is a line reprsenting a string.

lines that are meant to be strings must be only made up of ONLY the following characters AND must end with a vertical bar:

newline/carriage return: "\n"
tab: ""\t"
*only* the uppercase letters that belong to the set of bass string ids {G, D, A, E}
vertical bar: "|"
hyphen: "-"
space: " "
digits (0-9)
"""
def checkStringLine(line):
    if len(line) == 0:
        return False
    return len(line.strip("\tGDAE|-()0123456789 ")) == 0 and line.endswith("|")

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
    count = 0
    lastNoteExt = 0
    for line in lines:
        sLine = line.strip("\n")
        arr = list(sLine)
        if hasTiming:
            if count % 5 == 0:
                if checkNoteLine(sLine):
                    notes.extend(arr)
                    count += 1
                    lastNoteExt = len(arr)
            else:
                if checkStringLine(sLine):
                    if count % 5 == 1:
                        gString.extend(arr)
                        # need to update the last addition to the notes list to add spaces to make the timing line of the input file have the same length as the g-string below it
                        # otherwise, for input files where tabs may be on separate lines, the notes' timings would not be above the 1st digit of the fret of the note corresponding
                        # to it. This is what is needed in buildSong in order to properly parse the input data and load it into a Song object.
                        for i in range(lastNoteExt, len(arr)):
                            notes.append(" ")
                    elif count % 5 == 2:
                        dString.extend(arr)
                    elif count % 5 == 3:
                        aString.extend(arr)
                    elif count % 5 == 4:
                        eString.extend(arr)
                    count += 1
                    # all conditions covered
        else:
            if checkStringLine(sLine):
                if count % 4 == 0:
                    gString.extend(arr)
                elif count % 4 == 1:
                    dString.extend(arr)
                elif count % 4 == 2:
                    aString.extend(arr)
                elif count % 4 == 3:
                    eString.extend(arr)
                count += 1
    if (hasTiming and count % 5 != 0) or (hasTiming and count % 4 != 0):
        raise TabFileException(count)

"""
Reads the input tab file and loads it into its initial representation as 5 arrays (4 for the guitar strings, 1 for the timing symbols), builds the Song using the
above method, and then creates the output HTML file.

params:
logger - Logger object to report output

Raises TabException if no input file can be found.
"""
def run(logger):
    try:
        if len(argv) < 2:
            raise TabException("No input file can be found.")

        inFilename = argv[1]
        logger.log("Successfully located input file {0}. Beginning tab-reading program...".format(inFilename))

        rdr = ConfigReader()
        if rdr.readConfigFile():
            logger.log("Configuration file was loaded successfully.")
        else:
            logger.log(msg="Configuration file was not found. Default configuration file was created and read instead.", type=Logger.WARNING)

        hasTiming = rdr.getTiming()

        Slice.loadLengths()

        notes = list()
        gString = list()
        dString = list()
        aString = list()
        eString = list()

        try:
            with open(inFilename) as inputFile:
                lines = inputFile.readlines()
            logger.log("Input tab file {0} was opened and closed successfully.".format(inFilename))
        except IOError as i:
            raise TabException("I/O Error with opening tab file: " + str(i))

        loadLinesIntoLists(lines, notes, gString, dString, aString, eString, hasTiming)
        logger.log("Data in input tab file {0} was loaded successfully into array representation. ".format(inFilename))

        song = Song(rdr.getGapsize())
        buildSong(song, notes, gString, dString, aString, eString)
        logger.log("Data in input tab file {0} was parsed and loaded into a Song successfully. ".format(inFilename))

        pathNoExt = argv[1][:-4]
        outFilename = pathNoExt+"_staff.html"
        try:
            with open(outFilename, "w+", encoding="utf-8") as outFile:
                outFile.write("<!DOCTYPE HTML><html><title>" + pathNoExt[pathNoExt.rfind("\\")+1:]+" staff </title><body><pre>" + str(song) + "</pre></body></html>")
            logger.log("Output HTML file {0} was opened and data in Song created from input tab file {1} was written successfully before closing.".format(outFilename, inFilename))
        except IOError as i:
            raise TabException("I/O Error with creating HTML file: " + str(i))

    except TabFileException as t:
        logger.log(msg=str(t), type=Logger.ERROR)
    except TabConfigurationException as c:
        logger.log(msg=str(c), type=Logger.ERROR)
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
finally:
    logger.close()
