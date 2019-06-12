"""
This file consists of the functions that are used in parsing the input tab file and loading its data into music type objects. Its primary method is 'buildSong()' while the others are helper methods that are meant to assist it. This is the sole method used by tabReader.py.

Compatibility Note: This file is what makes this project not incompatible with Python 2. Since Python 3 strings are represented in Unicode, the string.translate() method was changed. This method now requires a single argument, a translation table, which is different from the string.translate() method in Python 2.
While string.strip() seems to work for the purposes of these methods, it appears to be much slower than string.translate() as each combination of the passed arguments is run through and stripped.

author: Chami Lamelas
date: Summer 2019
"""

from typeLibrary import Song, Measure, Slice
from exceptionsLibrary import TabFileException

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
Returns whether or not a line - with the below pre-conditions - is a "simple" string line from the input tab file.

pre-conditions:
(i) The line has at least 1 non-whitespace character
(ii) The line has been stripped on the end of whitespace

params:
line - a line that is to be checked
playingLegend - a set of characters that are allowed to be in string lines (see README)

Simple string lines must satisfy the following properties:

(a) The first non-whitespace character must be G, D, A, or E followed by a "|" or just be "|"
(b) Following either case of (a), a sequence of only the following characters:

vertical bar: "|"
hyphen: "-"
digits (0-9)
any characters in the playing legend

(c) The last non-whitespace character must be a "|"
(d) Be at least 3 characters long, not counting the whitespace at either end.
"""
def checkSimpleStringLine(line, playingLegend):
    checkSet = set("|-0123456789").union(playingLegend)
    if len(line) < 3:
        return False
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
    measure = Measure() # temp. var. to store Measure currently being built. It is reset after being added to 'song'
    i = start # 'i' iterates over portion of provided lists; that is, the interval ['start', 'end']
    while i <= end:
        slice = Slice() # Slice being built from the data at index 'i' in the lists
        skip1 = False # determines whether a 2-digit fret number has been detected, and if so skip the next index in the lists

        # parse the Notes from all 4 string lists, and update 'skip1'
        if parseNote(gString, i, slice, "G"):
            skip1 = True
        if parseNote(dString, i, slice, "D"):
            skip1 = True
        if parseNote(aString, i, slice, "A"):
            skip1 = True
        if parseNote(eString, i, slice, "E"):
            skip1 = True

        if slice.isEmpty():
            # the following 2 if-statements can be summarized as follows: if the string list entry at index 'i' is a measure line, then the entries at 'i' for all the other 3 string lists must also be a measure line. Otherwise, raise an error
            if gString[i] == "|" or dString[i] == "|" or aString == "|" or eString[i] == "|":
                if gString[i] != "|" or dString[i] != "|" or aString[i] != "|" or eString[i] != "|":
                    raise TabFileException("improper measure line detected", "Not all string lists have a \"|\" at column " + str(i), line=i)
                if not measure.isEmpty():
                    song.addMeasure(measure)
                    measure = Measure()
                # else don't add empty Measures to the Song
            # else all the characters in the string lists at this index don't matter: they are members of legend or are "-"
        else:  # if user specified that the timing wasn't supplied, the notes array was never filled
            if notes: # if timing was supplied, set the Slice's length to its raw time at notes[i] and tie it if notes[i-1]="+" and apply any dots that follow notes[i]
                slice.setLength(notes[i])
                if i > 0 and notes[i - 1] == Song.tieSymbol:
                    lastSlice.tie(slice)
                j = i+1
                while j < len(notes) and notes[j] == Song.dotSymbol:
                    slice.applyDot()
                    j = j + 1
            # else timing hasn't been loaded, do nothing

            measure.addSlice(slice) # regardless, add the Slice to the temp. measure
            lastSlice = slice # update last Slice for future ties

        # apply skip so the next list entries to be read - signified by index 'i' - is updated properly
        if skip1:
            i += 2
        else:
            i += 1
    return lastSlice # return updated last Slice to be added to 'song'

"""
Given a line from the tab file, shortens it by removing extra text on both ends as long as there is at least a 3 character string data segment. That is a 3 character segment with "|" on both ends.
This is the shortest possible string data segment as outlined in the doc. for 'checkStringLine()'

param:
line - a non-simple string line

pre-condition: as mentioned above, line must be stripped on both ends of whitespace

Returns a 2-element list. The first element is the updated line and the 2nd is the number of elements stripped from the front of the line. This is used in 'buildSong()'
"""
def shortenNonSimpleString(line):
    startingBar = line.find("|")
    endingBar = line.rfind("|")
    if endingBar - startingBar >= 2:
        return [line[startingBar:endingBar+1], startingBar]
    else:
        return [line, 0]

"""
Builds a Song given the list of lines read from the input file and configuration data loaded by the method run(). At the end of
this method, if it completes successfully, the data from the input tab file will have been parsed and stored appropriately in
Song, Measure, and Slice objects.

params:
lines - list of lines read from input file
song - Song object that will be loaded with Measures and Slices
rdr - ConfigReader that holds program config. data
loadedLines - array used to report info. on progress of parsing 'lines' to main method 'run()' since Python lists are passed by ref.
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
def buildSong(lines, song, rdr, loadedLines):
    notes = list() # list that holds timing info
    gString = list() # list that holds data from g-string (fret numbers, measure lines, dashes, and anything in 'legend')
    dString = list() # list that holds data from d-string ("                                                           ")
    aString = list() # list that holds data from a-string ("                                                           ")
    eString = list() # list that holds data from e-string ("                                                           ")

    # load repeatedly called config. options into tmp. variables so internal checks by ConfigReader aren't done each timing the setting needs to be retrieved (see ConfigReader's doc.). This is safe as it is known that the config. options will not be edited in this method
    hasTiming = rdr.isTimingSupplied()
    hasExtra = rdr.isExtraTextPresent()
    tabSpacing = rdr.getTabSpacing()
    playingLegend = rdr.getPlayingLegend()
    hasSimpleStrings = rdr.hasSimpleStringLines()

    lastSlice = Slice() # holds last Slice to be added to the Song. This is kept updated by calls to 'updateSong()'
    nextUpdate = 0 # the helper method 'updateSong()' loads portions of the lists at a time into 'song'. This var. signifies the beginning of the next portion to be added to 'song'
    while loadedLines[0] < len(lines): # iterates over lines to be read
         # (1) All whitespace should be stripped from the end of any line. In the case of empty lines, this will convey the same message as stripping both ends of the line of whitespace. For timing lines,
        # this allows the proper number of spaces to be added at the end of notes line as explained in the method doc. for this method. For string lines, this will solve the issue
        # of different string lines having different amounts of whitespace at the end and making sure they too have the same length as the timing lines with the new spaces.
        # (2) In order to ensure that the 5 lists above are the same length, all tabs must be converted into spaces. That way, the notes list can be properly expanded or reduced to maintain
        # note alignment (on string lines) with their timing symbols (on timing lines above them).
        sLine = lines[loadedLines[0]].rstrip().expandtabs(tabSpacing)
        if len(sLine) == 0: # 'sLine' was empty
            loadedLines[0] += 1
            if (hasTiming and loadedLines[1] % 5 == 0) or (not hasTiming and loadedLines[1] % 4 == 0): # this makes sure that only empty lines that are not in between string/timing lines are added to the extra text in 'song'
                song.placeExtraLine(" ")
            # else: this is an empty line in between strings, ignore it
            continue

        if hasTiming: # if user has specified that timing was supplied -> read lines in groups of 5, and note lines must be checked for
            if loadedLines[1] % 5 == 0: # if any multiple of 5 lines has been read, the next line should be a note line if input file is valid.
                arr = list(sLine)
                if not hasExtra or checkNoteLine(sLine): # if 'song' doesn't have extra text or if 'sLine' is a valid note-timing line, add it to the notes list and update 'loadedLines[1]'
                    nextUpdate = len(notes) # set 'nextUpdate' to be the first index of the new data added to the timing list. It is assumed by previous calls to 'updateSong()' that the data from all 5 lists have been read up to this index. Otherwise the error below would have been raised
                    notes.extend(arr)
                    loadedLines[1] += 1
                else: # otherwise, record it as extra text
                    song.placeExtraLine(sLine)
            else:
                init = len(sLine)
                sLine = sLine.lstrip()
                frontTrimSize = init - len(sLine) # stores how much has been trimmed from the front of the line
                if not hasSimpleStrings: # can use 'checkSimpleStringLine()' to check 'sLine' in this case, but first remove extra text from ends.
                    out = shortenNonSimpleString(sLine)
                    sLine = out[0]
                    frontTrimSize += out[1]
                arr = list(sLine)
                if not hasExtra or checkSimpleStringLine(sLine, playingLegend): # if 'song' doesn't have any extra text or if 'sLine' is a valid string line, add it to its appropriate string list and update 'loadedLines[1]'
                    if loadedLines[1] % 5 == 1:
                        gString.extend(arr)
                        # in the cases where there is extra text or whitespace before string lines, there must also be whitespace in front of the timing line corresponding to those string lines (i.e. above them in the tab file). The following loop removes
                        # the correct number of spaces from the beginning of the latest extension to the notes list by calculating how much was stripped from the front of sLine. This is necessary to realign the timing symbols with the notes on the string
                        # lines below.
                        for i in range(0, frontTrimSize):
                            del notes[nextUpdate]
                         # need to update the last addition to the notes list to add spaces to make the timing line of the input file have the same length as the g-string list below it
                        # otherwise, for input files where tabs may be on separate lines, the notes' timings would not be above the 1st digit of the fret of the note corresponding
                        # to it. This is what is needed in the helper method 'updateSong()' in order to properly parse the input data and load it into a 'song'
                        for i in range(len(notes), len(gString)):
                            notes.append(" ")
                    elif loadedLines[1] % 5 == 2:
                        dString.extend(arr)
                    elif loadedLines[1] % 5 == 3:
                        aString.extend(arr)
                    elif loadedLines[1] % 5 == 4:
                        eString.extend(arr)
                        # check that the string lists and timing list all have the same length before trying to load the list data into music type objects. Otherwise, 'updateSong()' may run into an indexing error
                        if len(gString) != len(dString) or len(gString) != len(aString) or len (gString) != len(eString) or len(gString) != len(notes):
                            raise TabFileException("lists not loaded properly", "The lists holding the strings (lengths = {0}, {1}, {2}, {3}) and the list holding the timing ({4}) must have the same length.".format(len(gString), len(dString), len(aString), len(eString), len(notes)), line=loadedLines[0])
                        lastSlice = updateSong(song, nextUpdate, len(gString)-1, notes, gString, dString, aString, eString, lastSlice)
                    loadedLines[1] += 1
                else: # Otherwise, record it as extra text
                    song.placeExtraLine(sLine)
        else: # the user has specified that no timing was supplied -> read lines in groups of 4
            init = len(sLine)
            sLine = sLine.lstrip()
            diff = init - len(sLine)
            if not hasSimpleStrings: # can use 'checkSimpleStringLine()' to check 'sLine' in this case, but first remove extra text from ends.
                out = shortenNonSimpleString(sLine)
                sLine = out[0]
                diff += out[1]
            arr = list(sLine)
            if not hasExtra or checkSimpleStringLine(sLine, playingLegend): # if 'song' doesn't have extra text or if 'sLine' is a valid string line, add it to its appropriate string list and update 'loadedLines[1]'
                if loadedLines[1] % 4 == 0:
                    nextUpdate = len(gString) # set 'nextUpdate' to be the first index of the new data added to the g-string list. It is assumed by previous calls to 'updateSong()' that the data from all 4 lists have been read up to this index. Otherwise the error below would have been raised
                    gString.extend(arr)
                elif loadedLines[1] % 4 == 1:
                    dString.extend(arr)
                elif loadedLines[1] % 4 == 2:
                    aString.extend(arr)
                elif loadedLines[1] % 4 == 3:
                    eString.extend(arr)
                    # check that the string lists have the same length before trying to load the list data into music type objects. Otherwise, 'updateSong()' may run into an indexing error
                    if len(gString) != len(dString) or len(gString) != len(aString) or len(gString) != len(eString):
                        raise TabFileException("lists not loaded properly", "The lists holding strings (lengths = {0}, {1}, {2}, {3}) must have the same length.".format(len(gString), len(dString), len(aString), len(eString)), line=loadedLines[0])
                    lastSlice = updateSong(song, nextUpdate, len(gString)-1, notes, gString, dString, aString, eString, lastSlice)
                loadedLines[1] += 1
            else:
                song.placeExtraLine(sLine)
        loadedLines[0] += 1 # mark that a line has been read

    if (hasTiming and loadedLines[1] % 5 != 0) or (not hasTiming and loadedLines[1] % 4 != 0): # if timing was supplied, count should be a multiple of 5 and if not it should be a multiple of 4
        errorMsg = ""
        if hasTiming:
            errorMsg = "The number of lines interpreted as strings and timing identifiers ({0}) is incorrect, should be a multiple of 5".format(loadedLines[1])
        else:
            errorMsg = "The number of lines interpreted as strings ({0}) is incorrect, should be a multiple of 4".format(loadedLines[1])
        raise TabFileException("input file line count incorrect", errorMsg)
