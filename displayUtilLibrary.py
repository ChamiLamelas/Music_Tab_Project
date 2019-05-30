"""
This file holds classes that are used for displaying the data held in Slices, Measures, and Songs in tableture form in an HTML file.

StaffString - a special "vertical" String type used for better display in tablature form.

In general, Slice, Measure, and Song objects all have StaffString representations.

author: Chami Lamelas
date: Summer 2019
"""

from exceptionsLibrary import StaffException, StaffOutOfBoundsException

"""
This class is a vertical collection of Strings and concatenation is done through the union() method which given 2 StaffStrings combines each row horizontally. The
class has only 1 attribute:

buf - a vertical buffer, a list of Strings
width - number of characters in each row of the buffer

The class has additional static variables:

STAFF_HEIGHT - the height of a staff, that is the number of available staff positions. This depends on the span of the staff which can be played on a bass.
BASS_CLEF_BTM - the staff position marking the bottom of the bass clef
BASS_CLEF_TOP - the staff position marking the top of the bass clef
newLineStaffString - the StaffString version of "\n" for regular Strings, initialized by a script at the end of the file.
DEFAULT_STR = the default value of "str", a constructor parameter discussed below.
"""
class StaffString:
    STAFF_HEIGHT = 33 # may need adjusting
    BASS_CLEF_BTM = STAFF_HEIGHT - 3
    BASS_CLEF_TOP = STAFF_HEIGHT - 11
    newLineStaffString = None
    DEFAULT_STR = "default"

    """
    By default, constructs a StaffString that is, it is just "-" and " " that spans the bass clef and " " for the rest of the StaffString's entries. In the type library, the
    default parameters are typically used. However, 2 parameters allow changes to the StaffString construction. If you wish the entries to not just be "-" and " " in the rows of
    the StaffString spanning the height of the bass clef, use the parameter "str". To have str appear throughout the entire height of the StaffString, set the bass cleff height
    restriction to be off by setting "restrict" equal to False.

    params:
    str - described above.
    restrict - described above

    Raises a StaffException if len(str) > 1 when str is not the default value.
    Use union() to create StaffStrings where each row has a length of more than 1. On its own, StaffString objects represent a slice of the staff.
    """
    def __init__(self, str=DEFAULT_STR, restrict=True):
        if str != StaffString.DEFAULT_STR and len(str) > 1:
            raise StaffException("construction", "string too large;", str)

        self.width = 1
        if str != StaffString.DEFAULT_STR:
            self.width = len(str)

        self.buf = list()
        for i in range(0, StaffString.STAFF_HEIGHT):
            if restrict: # fill only lines within height of the bass clef
                if i <= StaffString.BASS_CLEF_BTM and i >= StaffString.BASS_CLEF_TOP:
                    if str == StaffString.DEFAULT_STR:
                        if i % 2 == 0:
                            self.buf.append("-")
                        else:
                            self.buf.append(" ")
                    else:
                        self.buf.append(str)
                else:
                    self.buf.append(" ")
            else: # fill entire buffer
                self.buf.append(str)

    """
    Checks if an index falls within the appropriate bounds of a StaffString.

    Raises a StaffOutOfBoundsException if index is out of bounds.
    """
    def checkIndex(index):
        if index < 0 or index >= StaffString.STAFF_HEIGHT:
            raise StaffOutOfBoundsException("index out of bounds", index)

    """
    Returns the String at a specified row of the StaffString

    params:
    index - index of the desired row

    Raises a StaffOutOfBoundsException if checkIndex(index) fails.
    """
    def getRowAtIndex(self, index):
        StaffString.checkIndex(index)
        return self.buf[index]

    """
    Sets a row in the StaffString to a given String.

    params:
    str - a given String
    index - row of StaffString to update to str

    Raises a StaffOutOfBoundsException if str is too long or too short to be placed in this StaffString or if StaffString.checkIndex() fails.
    Raises a StaffException if str=="\n". Use union(StaffString.newLineStaffString) instead to
    """
    def updateIndexToStr(self, index, str):
        if len(str) != self.width:
            raise StaffOutOfBoundsException("cannot update row to provided String's size", len(str))
        if str == "\n":
            raise StaffException("updating a row", "Illegal \"str\" value. If you are trying to put StaffStrings on separate lines, union this StaffString with StaffString.newLineStaffString to get the same affect as appending \"\n\" to a regular String. Placing carriage returns in a StaffString is not allowed.", "\n")
        StaffString.checkIndex(index)
        self.buf[index] = str

    """
    Concatenates 2 StaffStrings horizontally.

    params:
    other - another StaffString
    """
    def union(self, other):
        if other is None:
            raise StaffException("union", "Cannot union this StaffString with \"other\".", other)
        newBuf = list()
        self.width += other.width
        for i in range(0, StaffString.STAFF_HEIGHT):
            newBuf.append(self.buf[i] + other.buf[i])
        self.buf = newBuf

    """
    Returns True if a given row in the StaffString is empty except for whitespace characters.

    params:
    index - the index of the desired row
    """
    def rowIsEmpty(self, index):
        return len(self.buf[index].strip("\n\t ")) == 0

    """
    Returns a String representation of this StaffString object.
    """
    def __str__(self):
        out = list()
        # Trim the output: that is, all empty rows above and below the highest and lowest non-empty rows of the StaffString are ignored. Trimming is stopped at the bounds of the bass clef.
        i = StaffString.STAFF_HEIGHT - 1
        while i > StaffString.BASS_CLEF_BTM and self.rowIsEmpty(i):
            i -= 1
        j = 0
        while j < StaffString.BASS_CLEF_TOP and self.rowIsEmpty(j):
            j += 1
        lastNewLine = -1 # tracks the index of the last detected newline column (note - newline characters will only appear in columns due to StaffString.newLineStaffString)
        w = 0 # iterates over the width of the StaffString
        while w < self.width:
            for k in range(j, i + 1): # Iterates over rows that have been chosen by trimming process
                w = lastNewLine + 1 # start iteration at next non-newline column
                ln = "" # temp. var. that holds the line to be added to the output, constructed in the following loop which iterates column by column until either the width has been reached or a newline col. has been reached
                while w < self.width and self.buf[k][w] != "\n":
                    ln += self.buf[k][w]
                    w += 1
                out.append(ln)
            if w < self.width: # if it was the latter while condition that terminated the loop, record the last newline col.
                lastNewLine = w
            out.append("\n") # add a separater line to the output that has the "newline" effect on regular strings
        return "\n".join(out) # return a string that puts all the created lines on separate lines

"""
Script that loads the StaffString version of "\n" after the class has been compiled when this file is imported.
"""
StaffString.newLineStaffString = StaffString(str="\n", restrict=False)
