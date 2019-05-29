"""
This file provides a library of music types (or classes) that are used by tabReader.py.

Types:

Note - used by Slice, not used in tabReader.py
Slice - used by Measure
Measure - used by Song
Song - ultimately holds full conversion from tab to tablature.

In general, tabReader.py fills a Song with Slices and Measures and then gets the String representation of Song (which wraps a StaffString representation).

author: Chami Lamelas
date: Summer 2019
"""

from exceptionsLibrary import TabException, MeasureException, TabConfigurationException
from displayUtilLibrary import StaffString

"""
This class represents a musical note in 2 ways. It is constructed given a guitar representation, that is a combination of a string and a fret. It then converts
that into a staff-based representation. Thus, it has the following attributes:

string: the name of the note's string
fret: the note's fret on said string
staffPos: position of the note on the bass clef where 0 corresponds to the position of the lowest note on the guitar and can be as large as the highest note on
the staff
"""
class Note:
    """
    Constructs a Note given a string-fret representation (see class doc.).

    params:
    string - a string
    fret - a fret

    Raises a TabException if fret is not an integer in the range [0, 36] or string is not in the set {G, D, A, E}
    """
    # TODO hardcoded for standard tuning -> update
    def __init__(self, string, fret):
        try:
            MAX_FRET = 36 # may need update
            nFret = int(fret)
            if nFret < 0 or nFret > MAX_FRET:
                raise ValueError()
        except ValueError as v:
            raise TabException("Invalid fret value ({0}). Fret must be an integer in the range [0, {1}]".format(nFret, MAX_FRET))
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
            raise TabException("Invalid string name ({0}). Please review string identification.".format(string))

        # order holds the ordering of notes on the guitar starting with the letter corresponding to the lowest note on the bass and for a given index i in order,
        # counts[i] holds the number of staff positions (lines & spaces) before orders[i] on the staff.
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
        return self.staffPos < 0

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

In addition, the class has 3 static variables:

lengths - a dictionary that maps the symbols taken from the input file (the same as the kind stored in the object attribute symbol) to decimal values that represent
lengths of time.
unicode - a dictionary that maps the same set of symbols that are keys in lengths to unicode values that hold their representations to be displayed on the staff
output. Unicode values taken from https://unicode.org/charts/PDF/U1D100.pdf.
EMPTY_SLICE - used by StaffString in printing empty slices
"""
class Slice:

    lengths = dict()
    unicode = dict()
    NO_SYMBOL = "no symbol"

    """
    Static method used to load the 2 dictionaries from a set of lists. If the symbol list is None, then the dictionaries are loaded with default values.

    params:
    ids - list of symbols that appear in input file
    times - times corresponding to each symbol
    unicode - unicode values corresponding to each symbol
    """
    def loadLengths(ids=None, times=None, unicode=None):
        if ids is None:
            Slice.lengths["W"] = 1
            Slice.unicode["W"] = "\U0001D15D"
            Slice.lengths["H"] = 0.5
            Slice.unicode["H"] = "\U0001D15E"
            Slice.lengths["Q"] = 0.25
            Slice.unicode["Q"] = "\U0001D15F"
            Slice.lengths["E"] = 0.125
            Slice.unicode["E"] = "\U0001D160"
            Slice.lengths["S"] = 0.0625
            Slice.unicode["S"] = "\U0001D161"
        else:
            for i in range(0, len(ids)):
                Slice.lengths[ids[i]] = times[i]
                Slice.unicode[ids[i]] = unicode[i]
        Slice.unicode[Slice.NO_SYMBOL] = "\u2022"

    """
    Constructs an empty Slice object.

    Raises TabConfigurationException if Slice.lengths is empty.
    """
    def __init__(self):
        if not Slice.lengths:
            raise TabConfigurationException("Time lengths not loaded properly. Please review program set-up.")
        self.notes = list()
        self.length = -1
        self.numDots = 0
        self.nextDotLength = -1
        self.symbol = Slice.NO_SYMBOL
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
        if note.isSharp():
            self.hasSharp = True
        if abs(note.staffPos) > self.maxStaffPos:
            self.maxStaffPos = abs(note.staffPos)
        if abs(note.staffPos) < self.minStaffPos:
            self.minStaffPos = abs(note.staffPos)
        # print("string {0} fret {1} --> staff position {2}".format(string, fret, staffPos)) # DEBUG

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
    Checks if a symbol is one which is found in the input file.

    Raises a TabException if the symbol is not found
    """
    def checkSymbol(symbol):
        if symbol not in Slice.lengths:
            raise TabException("Symbol {0} not recognized".format(symbol))

    """
    Updates a symbol's attributes with a given length symbol taken from input file's set of length symbols.

    params:
    symbol - a given length symbol

    Raises a TabException if checkSymbol(symbol) fails (see above doc.)
    """
    def setLength(self, symbol):
        Slice.checkSymbol(symbol)
        self.symbol = symbol
        self.length = Slice.lengths[symbol]
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
    ledgerLine - ledger line associated with the Staff String
    """
    def fillLedgerLinesInToStaffStr(self, s, ledgerLine):
        i = StaffString.STAFF_HEIGHT - 1 - self.maxStaffPos
        if i % 2 != 0:
            i += 1
        while i < StaffString.BASS_CLEF_TOP:
            s.setIndex(i, ledgerLine)
            i += 2

        j = StaffString.STAFF_HEIGHT - 1 - self.minStaffPos
        if j % 2 != 0:
            j -= 1
        while j > StaffString.BASS_CLEF_BTM:
            s.setIndex(j, ledgerLine)
            j -= 2

    """
    Loads all of the notes in this Slice object's notes field into a StaffString provided a ledger line length associated with the StaffString.

    params:
    s - a StaffString object
    ledgerLineLength - a ledger line length associated with s
    """
    def loadNotesInToStaffStr(self, s, ledgerLineLength):
        SHARP = "\u266F"
        DOT = "\u00b7"

        for note in self.notes:
            str = Slice.unicode[self.symbol]
            fill = 1
            if note.isSharp():
                str += SHARP
                fill += 1
            for d in range(0, self.numDots):
                str += DOT
                fill += 1
            if note.staffPos % 2 == 0:
                str = "-"+str
                fill += 1
                for k in range(fill, ledgerLineLength):
                    str += "-"
            else:
                str = " "+str
                fill += 1
                for k in range(fill, ledgerLineLength):
                    str += " "
            s.setIndex(StaffString.STAFF_HEIGHT - 1 - abs(note.staffPos), str)

    """
    If this Slice object marks the beginning or end of a tie, given a StaffString object, this method attaches the ties to the appropriate places in the StaffString.

    params:
    s - a StaffString
    """
    def attachTiesToStaffStr(self, s):
        if self.tieBegins:
            BEGIN_TIE = "_" # "\U0001D175"
            for note in self.notes:
                idx = StaffString.STAFF_HEIGHT - 1 - abs(note.staffPos)
                s.setIndex(idx, s.getIndex(idx)[:-1] + BEGIN_TIE)

        if self.tieEnds:
            END_TIE = "_" # "\U0001D176"
            for note in self.notes:
                idx = StaffString.STAFF_HEIGHT - 1 - abs(note.staffPos)
                s.setIndex(idx, END_TIE + s.getIndex(idx)[1:])

    """
    Returns a StaffString representation of this Slice.
    """
    def getStaffStr(self):
        s = StaffString()
        ledgerLine = "---"
        s.union(StaffString())
        s.union(StaffString())
        if self.hasSharp:
            ledgerLine += "-"
            s.union(StaffString())
        for d in range(0, self.numDots):
            ledgerLine += "-"
            s.union(StaffString())

        self.fillLedgerLinesInToStaffStr(s, ledgerLine)
        self.loadNotesInToStaffStr(s, len(ledgerLine))
        self.attachTiesToStaffStr(s)
        return s

    """
    Used when a measure line must be made where rows are skipped corresponding to the notes in this Slice. That is, rows that should have been "|"" are replaced with
    "_" which are used in tying through a measure line.
    """
    def getCorrMeasureStaffStr(self):
        out = StaffString("|")
        for note in self.notes:
            out.setIndex(StaffString.STAFF_HEIGHT - 1 - abs(note.staffPos), "_")
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
        if self.length > 1:
            raise MeasureException("creating a Measure.", str(self.length) + " is not a valid Measure length.")
        # in the case of self.length < 1, for now will leave an empty space (don't know if this is formal though)

    """
    Returns the last Slice in the Measure.

    Raises a MeasureException if the Measure is empty.
    """
    def getLastSlice(self):
        if self.isEmpty():
            raise MeasureException("getting the last slice of a Measure.", " The Measure is empty.")
        return self.slices[len(self.slices)-1]

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
gapsize - the gapsize that separates the Slices that make up the Measures of this Song
"""
class Song:

    """
    Constructs an empty Song object.

    params:
    gapsize - a user-specified gapsize.

    Raises a TabConfigurationException if gapsize < 0
    """
    def __init__(self, gapsize):
        if gapsize < 0:
            raise TabConfigurationException("Unacceptable gapsize ({0}). The gapsize must be a nonnegative integer.".format(gapsize))
        self.measures = list()
        self.gapsize = gapsize

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
    DEPRECATED.

    Prints the Song to the console. Use only for debugging.
    """
    def print(self):
        out = "||"
        out += "|".join(map(str, self.measures))
        print(out + "||")

    """
    Returns a tableture String representation of this Song using StaffString utility class and its String represenation.
    """
    def __str__(self):
        MAX_ROW_WIDTH = 140
        out = StaffString("|")
        out.union(StaffString("|"))
        curr = StaffString(str="", restrict=False)
        for i in range(0, len(self.measures)):
            nextMeasure = self.measures[i].getStaffStr(self.gapsize)
            if curr.width + nextMeasure.width > MAX_ROW_WIDTH:
                out.union(curr)
                out.union(StaffString.newLineStaffString)
                if self.measures[i-1].getLastSlice().tieBegins:
                    out.union(self.measures[i-1].getLastSlice().getCorrMeasureStaffStr())
                else:
                    out.union(StaffString("|"))
                curr = StaffString(str="", restrict=False)
            curr.union(nextMeasure)
            if self.measures[i].getLastSlice().tieBegins:
                curr.union(self.measures[i].getLastSlice().getCorrMeasureStaffStr())
            else:
                curr.union(StaffString("|"))
        out.union(curr) # in case last row held in curr wasn't over max row width
        out.union(StaffString("|"))
        return str(out)
