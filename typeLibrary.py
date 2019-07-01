"""
This file provides a library of music types (or classes) that are used by parsingUtils.py.

Types:

Note - used by Slice
Slice - used by Measure
Measure - used by Song
Song - ultimately holds full conversion from tab to sheet music.

In general, parsingUtils.py fills a Song with Slices and Measures and then gets the String representation of Song (which wraps a StaffString representation).

author: Chami Lamelas
date: Summer 2019
"""

from exceptionsLibrary import TabException, MeasureException, TabConfigurationException, TabFileException
from displayUtils import StaffString
from enum import Enum
import re

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
    def __str__(self):
        return "{0}-string, fret {1}".format(self.string, self.fret)

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
        self.nextDotLength = self.length/2
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
        if self.length == Song.timingLegend[Song.NO_TIMING_SYMBOL]:
            raise TabException("Must have a timing length. Please use 'setLength()'.")
        self.numDots += 1
        self.length += self.nextDotLength
        self.nextDotLength /= 2

    """
    Returns number of timing dots that have been applied to this Slice.
    """
    def getDotCount(self):
        return self.numDots

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

    pre-condition: the time length associated with 'symbol' in 'Song.timingLegend' must be in [0, 1]. This is guaranteed by the definition of 'Song.timingLegend'.

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
    Returns whether or not the Slice is a rest
    """
    def isRest(self):
        return self.isEmpty() and self.length != Song.timingLegend[Song.NO_TIMING_SYMBOL][0]

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

        if self.isRest():
            str = Song.timingLegend[self.symbol][2]
            for d in range(0, self.numDots):
                str += DOT
            str = "-" + str + "-"
            s.updateIndexToStr(StaffString.BASS_CLEF_BTM - 4, str)
        else:
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
        return """
        Notes: {0}
        Symbol: {1}
        Length: {2}
        No. of dots: {3}
        Next dot length: {4}
        Max. staff pos.: {5}
        Min. staff pos.: {6}
        Has sharp: {7}
        Tie begins: {8}
        Tie ends: {9}
        Is empty: {10}
        Is rest: {11}
        """.format(",".join(map(str, self.notes)), self.symbol, self.length, self.numDots, self.nextDotLength, self.maxStaffPos, self.minStaffPos, self.hasSharp, self.tieBegins, self.tieEnds, self.isEmpty(), self.isRest())

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
This class represents the set of options of where extra text can be placed.

FOLLOWING_LINE - option that signfies extra text is on a line (with no string data) following a line with string data
START_OF_LINE - option that signifies extra text is at the beginning of this line (before some string data)
END_OF_LINE - option that signifies extra text is at the end of this line (after some string data)
"""
class ExtraTextPlacementOption(Enum):
    FOLLOWING_LINE = 0
    START_OF_LINE = 1
    END_OF_LINE = 2

"""
This class represents a Song, that is an ordered list of Measures. Song objects have the following attributes:

measures - a list of Measures
gapsize - The Song's gap size is the number of "-" or " " between 2 notes.
extraText - a list of lists that holds the extra text associated with the measures of this Song. For a given index i, 'extraText[i]', there is a 3-element list which is indexed using the Enum above 'ExtraTextPlacementOption'. That is,
    - index 0 holds the character string of extra text that occurs after the (i+1)th measure
    - index 1 holds the character string of extra text that occurs before the (i+1)th measure on the same line
    - index 2 holds the character string of extra text that occurs after the (i+1)th measure on the same line
Notes:
    - for 'extraText[0]', there should be no text on the same line as the 0th measure. That is, indexes 1, 2 should be empty.
    - However, for 'extraText[0]', there can be extra text following 0 measures, that is the extra text at the top of the input tab file (before the 1st measure)
    - when HAS_EXTRA is 'false', then 'extraText' only holds lines of whitespace for the purpose of maintaining the spacing provided in the input tab file

In addition, the class has some static variables:

timingLegend - a legend that maps timing symbols to 3-element lists.
    list[0] - symbol's associated timing length from [0, 1] (e.g. a quarter note has a timing length of 0.25, half note is 0.5, whole note is 1, etc.)
    list[1] - symbol's associated note Unicode code (e.g. if the symbol is for a quarter note, this would be the Unicode code for a quarter note)
    list[2] - symbol's associated rest Unicode code (e.g. if the symbol is for a quarter note, this would be the Unicode code for a quarter rest)
NO_TIMING_SYMBOL - key in unicode mapping that points to the unicode character to be placed on sheet music when timing for a Slice is not specified (has a list with 'list[0] = 0')
tieSymbol - character to be placed before a timing symbol that denotes the Slice with that timing is tied to the prior Slice
dotSymbol - character to be placed (can be more than once) after a timing symbol that denotes a Slice's timing is dotted
allowedTimingChars - characters allowed in timing lines, specified by 'TIMING_SYMBOLS' config. option
allowedPlayingChars - characters allowed in playing lines, specified by in part by 'PLAYING_LEGEND' config. option
EXTRA_TEXT_DELIMITER - in the output sheet music, the extra text at the beginning (and the end) of input string lines is placed above (and below) the output sheet music separated by this delimiter.
"""
class Song:
    EXTRA_TEXT_DELIMITER = ";"
    NO_TIMING_SYMBOL = "\u2022"
    timingLegend = {NO_TIMING_SYMBOL : [0, "\u2022"]} # if the length is specified it must be greater than 0. Hence the no timing length mapping = 0
    allowedTimingChars = r' '
    allowedPlayingChars = r'\d\-\|'
    tieSymbol = None
    dotSymbol = None

    """
    Loads timing data into static variables from 'TIMING_SYMBOLS' config. setting (see configUtils.py doc.).

    params:
    symbolList - 10 character string made up of unique characters with the following properties:
        symbolList[0] is the tie symbol
        symbolList[1] is the dot symbol
        symbolList[2] through symbolList[9] are the symbols for whole notes up to 128th notes in decreasing time length order.
    """
    def loadTimingDataFromSymbolList(symbolList):
        Song.tieSymbol = symbolList[0]
        Song.dotSymbol = symbolList[1]
        Song.timingLegend[symbolList[2]] = [1.0, "\U0001D15D", "\U0001D13B"]
        Song.timingLegend[symbolList[3]] = [0.5, "\U0001D15E", "\U0001D13C"]
        Song.timingLegend[symbolList[4]] = [0.25, "\U0001D15F", "\U0001D13D"]
        Song.timingLegend[symbolList[5]] = [0.125, "\U0001D160", "\U0001D13E"]
        Song.timingLegend[symbolList[6]] = [0.0625, "\U0001D161", "\U0001D13F"]
        Song.timingLegend[symbolList[7]] = [0.03125, "\U0001D162", "\U0001D140"]
        Song.timingLegend[symbolList[8]] = [0.015625, "\U0001D163", "\U0001D141"]
        Song.timingLegend[symbolList[9]] = [0.0078125, "\U0001D164", "\U0001D142"]
        Song.allowedTimingChars += re.escape(symbolList)

    """
    Loads playing legend info. from 'PLAYING_LEGEND' config. setting (see configUtils.py doc.).

    params:
    playingLegend - a character string holding additional allowed chars. in string lines.
    """
    def loadPlayingLegend(playingLegend):
        Song.allowedPlayingChars += re.escape(playingLegend)

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
        if measure.length > 1 or measure.length < 0:
            raise MeasureException("creating a Measure.", "{0} is not a valid Measure length. {1} Measure objects were created successfully.".format(measure.length, self.numMeasures()))
        # In the case where a Measure is made up of Slices with no timing info., the length of the Measure is 0.
        self.measures.append(measure)

    """
    Returns the number of Measures in this Song.
    """
    def numMeasures(self):
        return len(self.measures)

    """
    Using a Song object's 'extraText' attribute, records a new line of extra text appropriately given a certain number of measures and the extra text's placement with respect to the measure.

    params:
    line - a line of extra text
    measureCount - no. of the measure to be associated with it
    place - placement of line in relation to the measure

    Raises TabException if 'measureHasFollowingExtraText()' fails.
    """
    def placeExtraLine(self, line, measureCount, place: ExtraTextPlacementOption):
        while measureCount >= len(self.extraText):
            self.extraText.append(["", "", ""])
        if place.value == ExtraTextPlacementOption.FOLLOWING_LINE.value:
            if self.measureHasFollowingExtraText(measureCount):
                self.extraText[measureCount][ExtraTextPlacementOption.FOLLOWING_LINE.value] += "\n"
        self.extraText[measureCount][place.value] += line

    """
    Returns whether or not a given measure has an entry in 'extraText'. If measure < 0 or measure >= len(extraText), then there is no extra text entry associated with it. Review how extra text is indexed starting with an entry for 0 measures and can go up
    to an index for the no. of measures + 1 (see Song class attributes doc.).
    """
    def measureHasExtraTextEntry(self, measure):
        return measure >= 0 and measure < len(self.extraText)

    """
    Gets the extra text associated with a measure at a certain place (in relation to the measure).

    params:
    measure - which measure from which to retrieve the extra text from
    place - the place in relation to the measure

    If there is no extra text entry associated with that measure, then this returns None to differentiate with no extra text being associated with the measure (then it would return the empty char. string).
    """
    def getMeasureExtraTextAt(self, measure, place: ExtraTextPlacementOption):
        if not self.measureHasExtraTextEntry(measure):
            return None
        return self.extraText[measure][place.value]

    """
    Returns whether or not a given measure has extra text following it.

    params:
    measure - the given measure
    """
    def measureHasFollowingExtraText(self, measure):
        followingExtraText = self.getMeasureExtraTextAt(measure, ExtraTextPlacementOption.FOLLOWING_LINE)
        return followingExtraText is not None and followingExtraText != ""

    """
    Returns whether or not a given measure has extra text before it, on the same line.

    params:
    measure - the given measure
    """
    def measureHasStartingExtraText(self, measure):
        startingExtraText = self.getMeasureExtraTextAt(measure, ExtraTextPlacementOption.START_OF_LINE)
        return startingExtraText is not None and startingExtraText != ""

    """
    Returns whether or not a given measure has extra text after it, on the same line.

    params:
    measure - the given measure
    """
    def measureHasEndingExtraText(self, measure):
        endingExtraText = self.getMeasureExtraTextAt(measure, ExtraTextPlacementOption.END_OF_LINE)
        return endingExtraText is not None and endingExtraText != ""

    """
    Returns a sheet music String representation of this Song using StaffString utility class and its String represenation.

    Raises a TabFileException if the extra text in the file was not loaded properly.
    """
    def __str__(self):
        out = list() # list which will be joined to form output character string
        s = StaffString("", restrict=False) # temp. var. that will build up groups of Measures that is added to out before being reset. Resets are split up by additions from 'self.extraText' to the output list
        if len(self.extraText) > self.numMeasures() + 1:
            raise TabFileException("extra text loading failure", "The length of the extra text list ({0}) is not allowed. It must be less than or equal to {1}.".format(len(self.extraText), self.numMeasures() + 1))
        if self.measureHasFollowingExtraText(0): # if there is any extra text and there is extra text before the 1st measure, add it
            out.append(self.getMeasureExtraTextAt(0, ExtraTextPlacementOption.FOLLOWING_LINE) + "\n")
        for i in range(0, self.numMeasures()): # for each Measure in the Song, add it to 's' and place them and any extra text that may follow to the output list before resetting 's'
            if self.measureHasStartingExtraText(i + 1): # if there is extra text before the (i+1)th measure on the same line, place it above the measure's sheet music (hence the "\n")
                out.append(self.getMeasureExtraTextAt(i + 1, ExtraTextPlacementOption.START_OF_LINE) + "\n")
            if i == 0: # if this is the first Measure in the Song, put double bar lines at the beginning of the sheet music
                s.union(StaffString("|"))
                s.union(StaffString("|"))
            # for any Measure in the Song, add its StaffString to 's' followed by a bar line
            s.union(self.measures[i].getStaffStr(self.gapsize))
            s.union(StaffString("|"))
            if i == self.numMeasures() - 1: # if this is the last Measure in the Song, add an extra (ending) bar line.
                s.union(StaffString("|"))
            # if there is extra text after the (i+1)th measure (either on the same line or on the following line): add 's' to the output, followed by a new line, than any extra text that may follow - either on the same line or after - separated by "\n"
             # note: this accounts for any extra text that follows all the Measures in the Song because the loop ends when 'i' = 'self.numMeasures()' - 1 and thus 'i' + 1 = 'self.numMeasures()' and thus, in 'self.extraText' denotes the extra text that follows all the Measures in this Song.
            if self.measureHasEndingExtraText(i + 1) or self.measureHasFollowingExtraText(i + 1):
                out.append(str(s) + "\n")
                if self.measureHasEndingExtraText(i + 1):
                    out.append(self.getMeasureExtraTextAt(i + 1, ExtraTextPlacementOption.END_OF_LINE) + "\n")
                if self.measureHasFollowingExtraText(i + 1):
                    out.append(self.getMeasureExtraTextAt(i + 1, ExtraTextPlacementOption.FOLLOWING_LINE) + "\n")
                s = StaffString("|") # reset 's' for future measures being added
        # if the last measure stored in 's' was not followed by some extra text, then it would not have been added to the output in the prev. loop. If 's.width'=1, then nothing was ever added to it (note: in the loop it is reset to a width of 1 b/c it's set to
        # a measure line). In this case, add it to complete the output sheet music.
        if s.width > 1:
            out.append(str(s))
        return "".join(out)
