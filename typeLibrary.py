"""
This file provides a library of music types (or classes) that are used by tabParser.py.

Types:

Note - used by Slice
Slice - used by Measure
Measure - used by Song
Song - ultimately holds full conversion from tab to sheet music.

In general, tabParser.py fills a Song with Slices and Measures and then gets the String representation of Song (which wraps a StaffString representation).

author: Chami Lamelas
date: Summer 2019
"""

from exceptionsLibrary import TabException, MeasureException, TabConfigurationException, TabFileException
from displayUtilLibrary import StaffString

"""
This class represents a musical note in 2 ways. It is constructed given a guitar representation, that is a combination of a string and a fret. It then converts
that into a staff-based representation. Thus, it has the following attributes:

string: the name of the note's string
fret: the note's fret on said string
staffPos: position of the note on the bass clef where 0 corresponds to the position of the lowest note on the guitar and can be as large as the highest note on
the staff.
"""
class Note:
    """
    Constructs a Note given a string-fret representation (see class doc.).

    params:
    string - a string
    fret - a fret (is a String value)

    Raises a TabFileException if fret is not an integer in the range [0, 36] or string is not in the set {G, D, A, E}
    """
    # TODO hardcoded for standard tuning -> update
    def __init__(self, string, fret):
        try:
            MAX_FRET = 36 # may need update
            nFret = int(fret)
            if nFret < 0 or nFret > MAX_FRET:
                raise ValueError()
        except ValueError as v:
            raise TabFileException("invalid fret value ", "Fret cannot be \"{0}\", it must be an integer in the range [0, {1}]".format(nFret, MAX_FRET))
        halfsteps = -1 # number of halfsteps from lowest E on bass
        if string == "E":
            halfsteps = nFret
        elif string == "A":
            halfsteps = nFret + 5
        elif string == "D":
            halfsteps = nFret + 10
        elif string == "G":
            halfsteps = nFret + 15
        else:
            raise TabFileException("invalid string name", "\"{0}\" is not a valid string id. Please review string identification.".format(string))

        order = ["E","F","F#","G","G#","A","A#","B","C","C#","D","D#"]
        counts = [0, 1, 1, 2, 2, 3, 3, 4, 5, 5, 6, 6]

        # there are 7 staff position increments in order
        self.staffPos = int(halfsteps/len(order)) * 7 + counts[halfsteps % len(order)]
        if len(order[halfsteps % len(order)]) == 2:
            self.staffPos = -self.staffPos
        self.string = string
        self.fret = fret

    """
    Returns whether or not this note is a sharp.
    """
    def isSharp(self):
        return self.staffPos < 0 # based on implementation of __init__()

    """
    Provides a way to check the equality of 2 Notes.

    params:
    other - another Note

    Returns True if this Note is equal to other and False otherwise.
    """
    def __eq__(self, other):
        return self.staffPos == other.staffPos

    """
    Returns a string representation of this Note. Meant for debugging.
    """
    def __str__(self, other):
        return "{0}-string, {1} fret".format(self.string, self.fret)

"""
This class represents a slice of a Measure. A slice contains a group of Notes that are all played at the same time and for the same length. They are either all tied
or not and are either all dotted or not based on the timing notes seen at the top of the file. This is primarily to make staff writing easier. Slice objects have
the following attributes:

notes - a list of Notes in the Slice
length - time of Notes in Slice
numDots - number of dots associated with Slice, used to calculate time
symbol - symbol of each note in the Slice (taken from input file: e.g. Q=Quarter, W=Whole, H=Half, etc.). References to this are seen throughout the class doc.
maxStaffPos - largest staff position of the set of Notes in notes
minStaffPos - smallest staff position of the set of Notes in notes
hasSharp - truth value of the Slice containing a Note who is a sharp
tieBegins - truth value of the Slice being the start of a tie
tieEnds - truth value of the Slice being the end of a tie

Note: in StaffString object representation, a Note n at position n.staffpos will be at index = StaffString.STAFF_HEIGHT - 1 - n.staffPos. This is because moving bottom->top
in a StaffString corresponds to moving bottom->top in a Staff. Thus, placing n at index = n.staffPos in a StaffString would not do. This calculation is used throughout the
Slice class, which is why it is explained here.
"""
class Slice:
    """
    Constructs an empty Slice object.
    """
    def __init__(self):
        self.notes = list()
        self.symbol = Song.NO_TIMING_SYMBOL
        self.length = Song.timingLegend[self.symbol][0]
        self.numDots = 0
        self.nextDotLength = -1
        self.maxStaffPos = -1
        self.minStaffPos = StaffString.STAFF_HEIGHT
        self.hasSharp = False
        self.tieBegins = False
        self.tieEnds = False

    """
    Adds a Note to the Slice using string-fret representation (see Note doc.).

    params:
    string - a string
    fret - a fret

    Raises a TabException - see Note __init__() doc.
    """
    def addNote(self, string, fret):
        note = Note(string, fret)
        self.notes.append(note)
        # the following Slice attributes are updated for the purpose of future StaffString generation
        if note.isSharp():
            self.hasSharp = True
        if abs(note.staffPos) > self.maxStaffPos:
            self.maxStaffPos = abs(note.staffPos)
        if abs(note.staffPos) < self.minStaffPos:
            self.minStaffPos = abs(note.staffPos)

    """
    Applies a dot to the Slice. That is, the length of the Slice's time is increased accordingly.

    Raises TabException if object's length has not been set by a call to setLength() (see below)
    """
    def applyDot(self):
        if self.length == -1:
            raise TabException("Length not set.")
        self.numDots += 1
        self.length += self.nextDotLength
        self.nextDotLength /= 2

    """
    Checks if a length symbol is one which is found in the input file.

    Raises a TabException if the symbol is not found
    """
    def checkLengthSymbol(symbol):
        if symbol not in Song.timingLegend:
            raise TabFileException("symbol not recognized", "\"{0}\" is not a valid symbol. Please review symbol identification".format(symbol))

    """
    Updates a Slice's length with a given length symbol taken from input file's set of length symbols.

    params:
    symbol - a given length symbol

    pre-condition: the time length associated with 'symbol' in 'Song.timingLegend' must be in (0, 1].

    Raises a TabException if checkLengthSymbol(symbol) fails (see above doc.)
    """
    def setLength(self, symbol):
        Slice.checkLengthSymbol(symbol)
        self.symbol = symbol
        self.length = Song.timingLegend[symbol][0]
        self.nextDotLength = self.length/2

    """
    Returns whether or not the Slice is empty
    """
    def isEmpty(self):
        return len(self.notes)==0

    """
    Fills a provided StaffString with ledger lines above and below the bass clef based on the Slice's maximum and minimum staff positions. Thus, this method could
    leave the StaffString parameter (s) unchanged.

    params:
    s - a StaffString

    pre-condition: s has been prepared with the appropriate width.
    """
    def fillLedgerLinesInToStaffStr(self, s):
        ledgerLine = "" # fill the ledger line to be the StaffString's width
        for i in range(0, s.width):
            ledgerLine += "-"
        i = StaffString.STAFF_HEIGHT - 1 - self.maxStaffPos # upper ledger lines, working low->high in StaffString is equivalent to top->bottom in staff
        if i % 2 != 0:
            i += 1
        while i < StaffString.BASS_CLEF_TOP:
            s.updateIndexToStr(i, ledgerLine)
            i += 2
        j = StaffString.STAFF_HEIGHT - 1 - self.minStaffPos # lower ledger lines, working high->low in StaffString is equivalent to bottom->top in staff
        if j % 2 != 0:
            j -= 1
        while j > StaffString.BASS_CLEF_BTM:
            s.updateIndexToStr(j, ledgerLine)
            j -= 2

    """
    Loads all of the notes in this Slice object's notes field into a StaffString provided a ledger line length associated with the StaffString.

    params:
    s - a StaffString object

    pre-condition: s has been prepared with the appropriate width.
    """
    def loadNotesInToStaffStr(self, s):
        SHARP = "\u266F"
        DOT = "\u00b7"

        for note in self.notes:
            str = Song.timingLegend[self.symbol][1]
            fill = 1 # tracks how much of the StaffString's width has been filled. This is updated as sharps or dots are added to "str"
            if note.isSharp():
                str += SHARP
                fill += 1
            for d in range(0, self.numDots):
                str += DOT
                fill += 1
            # for what's left of str to be filled, add either "-" or " " depending on whether the note is on a line or space in the staff
            if note.staffPos % 2 == 0:
                str = "-"+str
                fill += 1
                for k in range(fill, s.width):
                    str += "-"
            else:
                str = " "+str
                fill += 1
                for k in range(fill, s.width):
                    str += " "
            s.updateIndexToStr(StaffString.STAFF_HEIGHT - 1 - abs(note.staffPos), str)

    """
    If this Slice object marks the beginning or end of a tie, given a StaffString object, this method attaches the ties to the appropriate places in the StaffString.

    params:
    s - a StaffString

    pre-condition: s has been prepared with the appropriate width
    """
    def attachTiesToStaffStr(self, s):
        if self.tieBegins: # if this Slice marks the beginning of a tie, update each index of the StaffString with a tie-beginning character
            BEGIN_TIE = "_" # "\U0001D175"
            for note in self.notes:
                idx = StaffString.STAFF_HEIGHT - 1 - abs(note.staffPos)
                s.updateIndexToStr(idx, s.getRowAtIndex(idx)[:-1] + BEGIN_TIE)
        if self.tieEnds: # if this Slice marks the ending of a tie, update each index of the StaffString with a tie-ending character
            END_TIE = "_" # "\U0001D176"
            for note in self.notes:
                idx = StaffString.STAFF_HEIGHT - 1 - abs(note.staffPos)
                s.updateIndexToStr(idx, END_TIE + s.getRowAtIndex(idx)[1:])

    """
    Returns a StaffString representation of this Slice.
    """
    def getStaffStr(self):
        s = StaffString()
        s.union(StaffString())
        s.union(StaffString())
        if self.hasSharp:
            s.union(StaffString())
        for d in range(0, self.numDots):
            s.union(StaffString())
        # now that a StaffString with a necessary width has been created, use helper methods to update it
        self.fillLedgerLinesInToStaffStr(s)
        self.loadNotesInToStaffStr(s)
        self.attachTiesToStaffStr(s)
        return s

    """
    Used when a measure line must be made where rows are skipped corresponding to the notes in this Slice. That is, rows that should have been "|"" are replaced with
    "_" which are used in tying through a measure line.
    """
    def getCorrMeasureStaffStr(self):
        out = StaffString("|")
        for note in self.notes: # replace indices corresponding to Notes in the Slice with "_"
            out.updateIndexToStr(StaffString.STAFF_HEIGHT - 1 - abs(note.staffPos), "_")
        return out

    """
    Returns a String representation of this Slice. This should only be used for debugging purposes.
    """
    def __str__(self):
        return "-".join(map(str, self.notes))

    """
    Ties this Slice to another Slice.

    Raises TabException if tie operation cannot be performed. This occurs when the lists of notes of the 2 Slices do not match.
    """
    def tie(self, slice):
        if len(slice.notes) != len(self.notes):
            raise TabException("Tie operation cannot be performed, varying numbers of notes: ({0}, {1})".format(len(self.notes), len(slice.notes)))
        for i in range(0, len(self.notes)):
            if slice.notes[i] != self.notes[i]:
                raise TabException("Tie operation cannot be performed; {0} and {1} are different notes.".format(slice.notes[i], self.notes[i]))
        self.tieBegins = True
        slice.tieEnds = True

"""
This class represents a Measure, that is an ordered list of Slices. Measure objects have the following attributes:

slices - a list of Slices
length - the length of the Measure, should be <= 1
"""
class Measure:

    """
    Constructs an empty Measure.
    """
    def __init__(self):
        self.slices = list()
        self.length = 0

    """
    Adds a new Slice to the list of Slices in this Measure.

    params:
    slice - a new Slice
    """
    def addSlice(self, slice):
        self.slices.append(slice)
        self.length += slice.length

    """
    Validates a Measure. That is, confirms its length is <= 1.

    Raises a MeasureException if this Measure's length > 1.
    """
    def validate(self):
        if self.length > 1 or self.length < 0:
            raise MeasureException("creating a Measure.", "{0} is not a valid Measure length.".format(self.length))
        # In the case where a Measure is made up of Slices with no timing info., the length of the Measure is 0.

    """
    Returns a StaffString representation of this Measure given a gapsize which is used to determine how many "-" separate Slices in the Measure.

    params:
    gapsize - number of "-" used to separate Slices.
    """
    def getStaffStr(self, gapsize):
        s = StaffString(str="", restrict=False)
        for i in range(0, len(self.slices)):
            s.union(self.slices[i].getStaffStr())
            if not self.slices[i].tieBegins and i + 1 < len(self.slices): # only put gaps lines when there is no tie and not at the end of a measure
                for i in range(0, gapsize):
                    s.union(StaffString())
        return s

    """
    Returns a String representation of this Measure. This is only to be used for debugging purposes.
    """
    def __str__(self):
        return " ".join(map(str, self.slices))

    """
    Returns True if there are no Slices in this Measure, False otherwise.
    """
    def isEmpty(self):
        return len(self.slices)==0

"""
This class represents a Song, that is an ordered list of Measures. Song objects have the following attributes:

measures - a list of Measures
gapsize - The Song's gap size is the number of "-" or " " between 2 notes. The extra text option specifies whether an input tab file whose data is to be loaded into this Song object contains extraneous text that are not string lines, timing lines, or whitespace.
extraText - a list of character strings that hold extraneous text AND whitespace if the user has set the extra text config. option to True or JUST whitespace if the option is False. For a given index 'i', 'extraText[i]; holds the extra text that occurs after 'i' Measures of the Song.

In addition, the class has some static variables:

timingLegend - a legend that maps timing symbols to their timing lengths (decimal value in (0, 1]) and Unicode codes (see README for more)
NO_TIMING_SYMBOL - key in unicode mapping that points to the unicode character to be placed on sheet music when timing for a Slice is not specified
tieSymbol - character to be placed before a timing symbol that denotes the Slice with that timing is tied to the prior Slice
dotSymbol - character to be placed (can be more than once) after a timing symbol that denotes a Slice's timing is dotted
allowedTimingChars - characters allowed in timing lines, specified by 'TIMING_SYMBOLS' config. option
allowedPlayingChars - characters allowed in playing lines, specified by in part by 'PLAYING_LEGEND' config. option
"""
class Song:
    NO_TIMING_SYMBOL = "\u2022"
    timingLegend = {NO_TIMING_SYMBOL : [0, "\u2022"]} # if the length is specified it must be greater than 0. Hence the no timing length mapping = 0
    allowedTimingChars = set({" "})
    allowedPlayingChars = set("-|0123456789")
    tieSymbol = None
    dotSymbol = None

    """
    Loads timing data into static variables from 'TIMING_SYMBOLS' config. setting (see configUtilLibrary.py doc.).

    params:
    symbolList - 10 character string made up of unique characters with the following properties:
        symbolList[0] is the tie symbol
        symbolList[1] is the dot symbol
        symbolList[2] through symbolList[9] are the symbols for whole notes up to 128th notes in decreasing time length order.
    """
    def loadTimingDataFromSymbolList(symbolList):
        Song.tieSymbol = symbolList[0]
        Song.dotSymbol = symbolList[1]
        Song.timingLegend[symbolList[2]] = [1.0, "\U0001D15D"]
        Song.timingLegend[symbolList[3]] = [0.5, "\U0001D15E"]
        Song.timingLegend[symbolList[4]] = [0.25, "\U0001D15F"]
        Song.timingLegend[symbolList[5]] = [0.125, "\U0001D160"]
        Song.timingLegend[symbolList[6]] = [0.0625, "\U0001D161"]
        Song.timingLegend[symbolList[7]] = [0.03125, "\U0001D162"]
        Song.timingLegend[symbolList[8]] = [0.015625, "\U0001D163"]
        Song.timingLegend[symbolList[9]] = [0.0078125, "\U0001D164"]
        Song.allowedTimingChars = Song.allowedTimingChars.union(set(symbolList))

    """
    Loads playing legend info. from 'PLAYING_LEGEND' config. setting (see configUtilLibrary.py doc.).

    params:
    playingLegend - a character string holding additional allowed chars. in string lines.
    """
    def loadPlayingLegend(playingLegend):
        Song.allowedPlayingChars = Song.allowedPlayingChars.union(set(playingLegend))

    """
    Constructs an empty Song object given a gap size and extra text setting (see class doc.).

    params:
    gapsize - a user-specified gapsize
    """
    def __init__(self, gapsize):
        self.measures = list()
        self.gapsize = gapsize
        self.extraText = list()

    """
    Adds a Measure to the Song.

    params:
    measure - a Measure

    Raises a MeasureException if measure.validate() fails (see this method's doc.)
    """
    def addMeasure(self, measure):
        measure.validate()
        self.measures.append(measure)

    """
    Returns the number of Measures in this Song.
    """
    def numMeasures(self):
        return len(self.measures)

    """
    Places an extra line into the Song's extra text storage.

    params:
    line - a line of extra text or whitespace
    """
    def placeExtraLine(self, line):
        if self.numMeasures() >= len(self.extraText):
            while self.numMeasures() > len(self.extraText):
                self.extraText.append("")
            self.extraText.append(line)
        else:
            self.extraText[self.numMeasures()] += "\n" + line

    """
    Returns a sheet music String representation of this Song using StaffString utility class and its String represenation.

    Raises a TabFileException if the extra text in the file was not loaded properly.
    """
    def __str__(self):
        if len(self.extraText) > self.numMeasures() + 1:
            raise TabFileException("extra text loading failure", "The length of the extra text list ({0}) is not allowed. It must be less than or equal to {1}".format(len(self.extraText), self.numMeasures() + 1))
        out = list() # list which will be joined to form output character string
        s = StaffString("", restrict=False) # temp. var. that will build up groups of Measures that is added to out before being reset. Resets are split up by additions from 'self.extraText' to the output list
        if len(self.extraText) > 0 and self.extraText[0] != "": # if there's extra text before 0 measures (i.e. at the beginning of the file), place that into the output first
            out.append(self.extraText[0])
        for i in range(0, self.numMeasures()): # for each Measure in the Song, add it to 's' and place them and any extra text that may follow to the output list before resetting 's'
            if i == 0: # if this is the first Measure in the Song, put double bar lines at the beginning of the sheet music
                s.union(StaffString("|"))
                s.union(StaffString("|"))
            # for any Measure in the Song, add its StaffString to 's' followed by a bar line
            s.union(self.measures[i].getStaffStr(self.gapsize))
            s.union(StaffString("|"))
            if i == self.numMeasures() - 1: # if this is the last Measure in the Song, add an extra (ending) bar line.
                s.union(StaffString("|"))
             # if there is extra text to be added after 'i' Measures, then 'self.extraText[i + 1]' != "". This is because 'self.measures' uses 0-based indexing where at ith iteration in the for-loop, i+1 Measures have been visited
             # if the above condition is true: add 's' to the output first, followed by the extra text, and then reset 's' for the next set of Measures to be added before the next time there is extra text to be added
             # note: this accounts for any extra text that follows all the Measures in the Song because the loop ends when 'i' = 'self.numMeasures()' - 1 and thus 'i' + 1 = 'self.numMeasures()' and thus, in 'self.extraText' denotes the extra text that follows all the Measures in this Song.
            if i + 1 < len(self.extraText) and self.extraText[i + 1] != "":
                out.append(str(s))
                out.append(self.extraText[i + 1])
                s = StaffString("|")
        if s.width > 1: # if there were any Measures that were not added in the above loop (because they weren't followed by extra text) add them
            out.append(str(s))
        return "\n".join(out)
