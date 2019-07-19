"""
This file consists of the functions that are used in parsing the input tab file and loading its data into music type objects. Its primary method is 'buildSong()' while the others are helper methods that are meant to assist it. This is the sole method used by tabReader.py.

author: Chami Lamelas
date: Summer 2019
"""

from typeLibrary import Song, Measure, Slice, ExtraTextPlacementOption
from exceptionsLibrary import TabFileException, TabConfigurationException
from configUtils import ConfigOptionID
import re

"""
Returns whether or not a given character string represents a timing line. That is, it is made entirely of the characters in 'Song.allowedTimingChars'.

params:
line - a character string

pre-condition:
'line' is not just whitespace. If this has not been checked, a line made up of whitespace would be counted as a valid timing line.
"""
def isTimingLine(line):
    return re.match(r'^[{0}]+$'.format(Song.allowedTimingChars), line) is not None

"""
Extracts the string data from a character string.

params:
line - a character string

The string data in 'line' is the 1st substring that begins with a "|", is made up entirely of characters in 'Song.allowedPlayingChars', and ends with a "|".
Extra text is allowed in 'line' and is assumed to be any text without a "|" before the string data segment above and any text following that same segment.

Note: extra text is not allowed to separate string data. Example: say 'line=|--1--| extra |--2--|'. The string data is identified as |--1--|.

If a substring with this pattern cannot be found, 'None' is returned.
"""
def extractStringData(line):
    return re.match(r'^([^\|]*)(\|[{0}]+\|)(.*)$'.format(Song.allowedPlayingChars), line)

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
        # else: fret is only 1 digit, do nothing
        slice.addNote(stringID, fret)
    # else: fret is not a valid fret, it is a "-" or "|", do nothing
    return skip

"""
Updates a Song object given a subset of the input data stored as a group of lists.

params:
song - a Song object to be updated
notes - list of timing info.
gString - representation of G-string
dString - representation of D-string
aString - representation of A-string
eString - representation of E-string
lastSlice - last Slice to be added to 'song'

pre-conditions:
if notes is not empty, it should have the same length as the string lists (gString, dString, aString, and eString)
if timing has been provided, then Song.timingLegend, Song.tieSymbol, and Song.dotSymbol should all have been updated from config. file

Returns the last Slice to be added to 'song', replaces param. 'lastSlice'

Raises TabConfigurationException if the Slice class' mapping from timing symbols to timing lengths was not loaded.
Raises TabFileException if helper method parseNote() fails, Slice.setLength() fails, or an improper measure line was detected. For the former 2, see their docs.
Raises TabException if Slice.applyDot() or Slice.tie() fail (see their doc.)
Raises MeasureException if Song.addMeasure() fails (see its doc.)
"""
def updateSong(song, notes, gString, dString, aString, eString, lastSlice):
    measure = Measure() # temp. var. to store Measure currently being built. It is reset after being added to 'song'
    i = 0
    while i < len(gString):
        slice = Slice() # Slice being built from the data at index 'i' in the lists
        skip1 = False # determines whether a 2-digit fret number has been detected, and if so skip the next index in the lists

        # at a given index 'i', if 'notes[i]' is a timing id but all the string lists at index 'i' hold hyphens, this indicates a rest. Therefore, by going through 'notes' and "looking below" at the string lists, rests can be accounted for
        # and the notes in the string lists can be added after if they are present (see 4 calls to 'parseNote()' below)
        if notes and notes[i] in Song.timingLegend:
            slice.setLength(notes[i])
            j = i + 1
            while j < len(notes) and notes[j] == Song.dotSymbol: # apply any following dots, as rests can be dotted
                slice.applyDot()
                j += 1     
        # otherwise, do nothing to the slice length 

        # parse the Notes from all 4 string lists, and update 'skip1' if notes[i] is a timing symbol or no timing was provided
        if (notes and notes[i] in Song.timingLegend) or not notes: 
            if parseNote(gString, i, slice, "G"):
                skip1 = True
            if parseNote(dString, i, slice, "D"):
                skip1 = True
            if parseNote(aString, i, slice, "A"):
                skip1 = True
            if parseNote(eString, i, slice, "E"):
                skip1 = True
        # otherwise, timing as provided and notes[i] isn't a timing symbol

        if i > 0 and notes and notes[i] in Song.timingLegend and notes[i - 1] == Song.tieSymbol: # only tie Slices after notes have been added, otherwise 'lastSlice' and 'slice' could have differing note counts as the count of 'slice' would be 0
            lastSlice.tie(slice)

        if slice.isRest() or not slice.isEmpty():
            measure.addSlice(slice)
            lastSlice = slice
        else:
            # the following 2 if-statements can be summarized as follows: if the string list entry at index 'i' is a measure line, then the entries at 'i' for all the other 3 string lists must also be a measure line. Otherwise, raise an error
            if gString[i] == "|" or dString[i] == "|" or aString == "|" or eString[i] == "|":
                if gString[i] != "|" or dString[i] != "|" or aString[i] != "|" or eString[i] != "|":
                    raise TabFileException("improper measure line detected", "Not all string lists have a \"|\" at the specified index.", line=i)
                if not measure.isEmpty():
                    song.addMeasure(measure)
                    measure = Measure()
                # else don't add empty Measures to the Song
            # else all the characters in the string lists at this index don't matter: they are members of the playing legend or are "-"

        # update 'i' accordingly with the knowledge that indexes with dots in 'notes' can be skipped (as there should be no notes below them) and can skip with a note with a double digit fret is encountered. See README for more info. on the latter case.
        if slice.getDotCount() > 0:
            i += slice.getDotCount()
        elif skip1:
            i += 2
        else:
            i += 1
    return lastSlice # return updated last Slice to be added to 'song'

"""
Compares a given character with a string name from Song.STRING_NAMES.

params:
chr - character to compare with a string name
name - a string name

Raises TabException if 'name' is not in Song.STRING_NAMES
Raises TabFileException if 'chr' != 'name'
"""
def checkChrToStringName(chr, name, line=0):
    if name not in Song.STRING_NAMES:
        raise TabException("Invalid string name argument '{0}'. Must be in {1}.".format(name, Song.STRING_NAMES))
    if chr != name:
        raise TabFileException("Invalid string name found.", "Unexpected string name '{0}' found in tab file. Expected string name {1}.".format(chr, name), line)

"""
Given the extra text from a beginning of a string line, removes the string name character from the end of it (if there is one), so that it is not saved as extra text in the output sheet music.

params:
text - a character string
name - the name that it should be if there is one (should be taken from 'Song.STRING_NAMES')
line - optional param. to help report error through 'checkChrToStringName()'

The 'name' must be the last character in 'text' and must follow 1 of the following 2 conditions:
(i) It is the only character in 'text'. This would be the case if the input tab line started with say "G" and was then followed by a "|" and some string data.
(ii) It follows at least 1 whitespace character. This would be the case if the input tab line had some other text before the string data segment. Say: Verse 1 G|1---0|
Here "Verse 1" is the only extra text and then there's a space between it and G.

Raises a TabFileException if (i) and (ii) are met but the last character doesn't equal 'name' or checkChrToStringName() fails.
"""
def removeStringName(text, name, line=0):
    if len(text) > 0: # check that there is actually some text captured from the beginning
        last = text[-1:].upper() # get uppercase ver. of last char. in 'text'
        if (len(text) > 1 and text[-2:-1].isspace()) or len(text) == 1: # checks properties (i)-(ii) from method doc.
            if not last.isspace():
                checkChrToStringName(last, name)
                return text[:-1] # strip last char and return
        # otherwise, 'last' is whitespace - ignore it
    # no extra text at front, nothing to do to 'text'
    return text

"""
Helper method that is used to update 'startingText' and 'endingText' by 'buildSong()'. That is, as each string is parsed, more extra text may be encountered at either end of the string. This method is used to add that extra text to the approriate character
string that collects the surrounding extra text.

params:
sameLineText - either 'startingText' or 'endingText' (and thus not None)
str - a string to be added to 'sameLineText'

Returns the updated 'sameLineText'
"""
def saveSameLineExtraText(sameLineText, str):
    str = str.strip() # strip any surrounding whitespace from 'str' that may have been used in the input tab file as formatting. Following the README guidelines, the extra text will now be stored in a list separated by the following delimiter.
    # note: this is not done for extra text that separates string & timing lines
    if str != "":
        if sameLineText != "": # if some extra text has been stored already, add the new extra text after the delimiter specified in the Song class.
            sameLineText += Song.EXTRA_TEXT_DELIMITER
        sameLineText += str
    return sameLineText

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
Raises TabConfigurationException if timing has been supplied but one of the following configuration settings were not read:
    - the mapping from timing symbols to length and unicode symbol
    - the tie symbol used in the input tab file
    - the dot symbol used in the input tab file
Furthermore, in the event of helper method updateSong() failing, the following exceptions could be raised:
    - TabFileException
    - TabException
    - MeasureException
    - TabConfigurationException
The reasons as to why these exceptions could be raised seemed to lengthy to add here. Instead, look at the doc. for 'updateSong()'.
"""
def buildSong(lines, song, rdr, loadedLines):
    notes = list() # list that holds timing info
    gString = list() # list that holds data from g-string (fret numbers, measure lines, dashes, and anything in 'legend')
    dString = list() # list that holds data from d-string ("                                                           ")
    aString = list() # list that holds data from a-string ("                                                           ")
    eString = list() # list that holds data from e-string ("                                                           ")

    # load repeatedly called config. options into tmp. variables so internal checks by ConfigReader aren't done each timing the setting needs to be retrieved (see ConfigReader's doc.). This is safe as it is known that the config. options will not be edited in this method
    hasTiming = rdr.getSettingForOption(ConfigOptionID.TIMING_SUPPLIED)
    hasExtra = rdr.getSettingForOption(ConfigOptionID.HAS_EXTRA)
    tabSpacing = rdr.getSettingForOption(ConfigOptionID.TAB_SPACING)
    keepExtra = rdr.getSettingForOption(ConfigOptionID.KEEP_EXTRA)

    if hasTiming and (len(Song.timingLegend) == 1 or not Song.tieSymbol or not Song.dotSymbol):
        raise TabConfigurationException(reason="program configuration failed. Timing legend was not loaded properly",line=ConfigOptionID.TIMING_SYMBOLS.value+1)

    startingText = "" # holds the extra text that occurs before - but on the same line as - the string data stored in notes, gString, dString, etc.
    endingText = "" # holds the extra text that occurs after - but on the same line as - the string data stored in notes, gString, dString, etc.
    lastSlice = Slice() # holds last Slice to be added to the Song. This is kept updated by calls to 'updateSong()'
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
                song.placeExtraLine(" ", song.numMeasures(), ExtraTextPlacementOption.FOLLOWING_LINE)  # since extra text lists are initialized to hold the empty string, make sure that an empty line is conveyed by at least 1 space or tab character. That way, it will actually be displayed in the output.
            # else: this is an empty line in between strings, ignore it
            continue

        if hasTiming: # if user has specified that timing was supplied -> read lines in groups of 5, and note lines must be checked for
            if loadedLines[1] % 5 == 0: # if any multiple of 5 lines has been read, the next line should be a note line if input file is valid.
                if isTimingLine(sLine):
                    notes = list(sLine)
                    loadedLines[1] += 1
                else: # otherwise, record it as a line of extra text (if desired by user) following the current number of measures in Song
                    if keepExtra:
                        song.placeExtraLine(sLine, song.numMeasures(), ExtraTextPlacementOption.FOLLOWING_LINE)
            else: # note at this point loadedLines[1] % 5 is in [1, 4]
                orig = len(sLine) # length of char. string before any changes
                arr = list()
                if hasExtra: # if there is extra text, extract string data into a match object with 3 groups: group 1 is the extra text before the string data, group 2 is the string data, and group 3 is the extra text after the string data
                    match = extractStringData(sLine)
                    if match is not None: # match object was created successfully, so string data was found.
                        arr = list(match.group(2))
                        if keepExtra:
                            # save the starting and ending extra text using helper 'saveSameLineExtraText()' by extracting capture group data from the regex match
                            startingText = saveSameLineExtraText(startingText, removeStringName(match.group(1), Song.STRING_NAMES[(loadedLines[1] % 5)-1], loadedLines[0] + 1))
                            endingText = saveSameLineExtraText(endingText, match.group(3))
                        #  else: this line does not have string data as the match was either None or not created properly
                else: # if there's no extra text, should only be whitespace at the start -> strip it
                    arr = list(sLine.lstrip())
                    if arr[0].isalpha(): # if the first non-whitespace char. in 'arr' is in the alphabet, it must be the correct string name corresponding to the current string to be parsed.
                        checkChrToStringName(arr[0].upper(), Song.STRING_NAMES[(loadedLines[1] % 5) - 1], loadedLines[0] + 1)
                if not hasExtra or match is not None:
                    if loadedLines[1] % 5 == 1:
                        gString = arr
                        trim = 0 # trim holds the no. of spaces to be removed from the beginning of 'notes' and is calculated from the match obj. if there is extra text or the amount of whitespace at the beginning of 'gString' if there's no extra text
                        if hasExtra:
                            trim = len(match.group(1))
                        else:
                            trim = orig - len(gString)
                        notes = notes[trim:] # using python 'list slicing', removes 'trim' spaces from the front of notes
                        # need to update the last addition to the notes list to add spaces to make the timing line of the input file have the same length as the g-string list below it
                        # otherwise, for input files where tabs may be on separate lines, the notes' timings would not be above the 1st digit of the fret of the note corresponding
                        # to it. This is what is needed in the helper method 'updateSong()' in order to properly parse the input data and load it into a 'song'
                        for i in range(len(notes), len(gString)):
                            notes.append(" ")
                    elif loadedLines[1] % 5 == 2:
                        dString = arr
                    elif loadedLines[1] % 5 == 3:
                        aString = arr
                    elif loadedLines[1] % 5 == 4:
                        eString = arr
                        # check that the string lists and timing list all have the same length before trying to load the list data into music type objects. Otherwise, 'updateSong()' may run into an indexing error
                        if len(gString) != len(dString) or len(gString) != len(aString) or len (gString) != len(eString) or len(gString) != len(notes):
                            raise TabFileException("lists not loaded properly", "The lists holding the strings (lengths = {0}, {1}, {2}, {3}) and the list holding the timing ({4}) must have the same length.".format(len(gString), len(dString), len(aString), len(eString), len(notes)), line=loadedLines[0])
                        # if there has been separating text associated with the current set of measures, then it would have been stored in the extra text entry for the measure that would follow the current last measure (see doc. for where separating text
                        # is added - some 15 lines or so below). If this is the case, add a newline character so that the starting text is placed below it.
                        if song.measureHasStartingExtraText(song.numMeasures() + 1):
                            startingText = "\n" + startingText
                        # place all the collected preceding extra text to be be before the 1st measure of the set of measures to be added.
                        # That is, before the measure that will come after the current last measure (indexed by Song.numMeasures() in Song.extraText)
                        # for more - see doc. for 'placeExtraLine()'
                        song.placeExtraLine(startingText, song.numMeasures() + 1, ExtraTextPlacementOption.START_OF_LINE)
                        startingText = "" # reset it now that the set of measures will be added
                        lastSlice = updateSong(song, notes, gString, dString, aString, eString, lastSlice)
                        # place all the collected preceding extra text to be be after the ;ast measure of the set of measures that were added.
                        # That is, after after the current last measure (indexed by Song.numMeasures() in Song.extraText)
                        # for more - see doc. for 'placeExtraLine()'
                        song.placeExtraLine(endingText, song.numMeasures(), ExtraTextPlacementOption.END_OF_LINE)
                        endingText = "" # reset it now that the set of measures have been added
                    loadedLines[1] += 1
                else: # otherwise, this is a line of extra text separating timing & string lines. Place it above the sheet music starting with 1st of the next set of measures to be added.
                      # That is, before the measure tjat will come after the current last measure (indexed by Song.numMeasures() in Song.extraText) for more - see doc. for 'placeExtraLine()'
                      # the set of measures will be added once 'updateSong()' is called after the G-string has been parsed.
                    if keepExtra:
                        song.placeExtraLine(sLine, song.numMeasures() + 1, ExtraTextPlacementOption.START_OF_LINE)
        else: # the user has specified that no timing was supplied -> read lines in groups of 4
            arr = list()
            orig = len(sLine) # len. of char. string before any changes
            if hasExtra: # if there is extra text, extract string data into a match object with 3 groups: group 1 is the extra text before the string data, group 2 is the string data, and group 3 is the extra text after the string data
                match = extractStringData(sLine)
                if match is not None: # match object was created successfully, so string data was found.
                    arr = list(match.group(2))
                    if keepExtra:
                        # save the starting and ending extra text using helper 'saveSameLineExtraText()' by extracting capture group data from the regex match
                        startingText = saveSameLineExtraText(startingText, removeStringName(match.group(1), Song.STRING_NAMES[loadedLines[1] % 4], loadedLines[0] + 1))
                        endingText = saveSameLineExtraText(endingText, match.group(3))
                # else: this line does not have string data as the match was either None or not created properly
            else: # if there's no extra text, should only be whitespace at the start -> strip it
                arr = list(sLine.lstrip())
                if arr[0].isalpha(): # if the first non-whitespace char. in 'arr' is in the alphabet, it must be the correct string name corresponding to the current string to be parsed.
                    checkChrToStringName(arr[0].upper(), Song.STRING_NAMES[loadedLines[1] % 4], loadedLines[0] + 1)
            if not hasExtra or match is not None:
                if loadedLines[1] % 4 == 0:
                    gString = arr
                elif loadedLines[1] % 4 == 1:
                    dString = arr
                elif loadedLines[1] % 4 == 2:
                    aString = arr
                elif loadedLines[1] % 4 == 3:
                    eString = arr
                    # check that the string lists have the same length before trying to load the list data into music type objects. Otherwise, 'updateSong()' may run into an indexing error
                    if len(gString) != len(dString) or len(gString) != len(aString) or len(gString) != len(eString):
                        raise TabFileException("lists not loaded properly", "The lists holding strings (lengths = {0}, {1}, {2}, {3}) must have the same length.".format(len(gString), len(dString), len(aString), len(eString)), line=loadedLines[0])
                    # if there has been separating text associated with the current set of measures, then it would have been stored in the extra text entry for the measure that would follow the current last measure (see doc. for where separating text
                    # is added - some 15 lines or so below). If this is the case, add a newline character so that the starting text is placed below it.
                    if song.measureHasStartingExtraText(song.numMeasures() + 1):
                        startingText = "\n" + startingText
                    # place all the collected preceding extra text to be be before the 1st measure of the set of measures to be added.
                    # That is, before the measure that will come after the current last measure (indexed by Song.numMeasures() in Song.extraText)
                    # for more - see doc. for 'placeExtraLine()'
                    song.placeExtraLine(startingText, song.numMeasures() + 1, ExtraTextPlacementOption.START_OF_LINE)
                    startingText = "" # reset it now that the set of measures will be added
                    lastSlice = updateSong(song, notes, gString, dString, aString, eString, lastSlice)
                    # place all the collected preceding extra text to be be after the ;ast measure of the set of measures that were added.
                    # That is, after after the current last measure (indexed by Song.numMeasures() in Song.extraText)
                    # for more - see doc. for 'placeExtraLine()'
                    song.placeExtraLine(endingText, song.numMeasures(), ExtraTextPlacementOption.END_OF_LINE)
                    endingText = "" # reset it now that the set of measures have been added
                loadedLines[1] += 1
            else:
                if keepExtra: # if the user desires to save extra text
                    # if the g-string hasn't been found, this is a line of extra text before a set of measures. In this case, record it as a line of extra text following the current number of measures in Song
                    if loadedLines[1] % 4 == 0:
                        song.placeExtraLine(sLine, song.numMeasures(), ExtraTextPlacementOption.FOLLOWING_LINE)
                    # otherwise, this is a line of extra text separating timing & string lines. Place it above the sheet music starting with 1st of the next set of measures to be added.
                    # That is, before the measure that will come after the current last measure (indexed by Song.numMeasures() in Song.extraText). for more - see doc. for 'placeExtraLine()'
                    # the set of measures will be added once 'updateSong()' is called after the G-string has been parsed.
                    else:
                        song.placeExtraLine(sLine, song.numMeasures() + 1, ExtraTextPlacementOption.START_OF_LINE)
        loadedLines[0] += 1 # mark that a line has been read

    if (hasTiming and loadedLines[1] % 5 != 0) or (not hasTiming and loadedLines[1] % 4 != 0): # if timing was supplied, count should be a multiple of 5 and if not it should be a multiple of 4
        errorMsg = ""
        if hasTiming:
            errorMsg = "The number of lines interpreted as strings and timing identifiers ({0}) is incorrect, should be a multiple of 5".format(loadedLines[1])
        else:
            errorMsg = "The number of lines interpreted as strings ({0}) is incorrect, should be a multiple of 4".format(loadedLines[1])
        raise TabFileException("input file line count incorrect", errorMsg)
