"""
This file provides a library of music exception types that are used throughout the project to better report errors to the user.

Exception Types:

TabException - general exception type for the project used to report general errors in the tab that cannot be reported more specifically
MeasureException - caused by the construction of a Measure whose length is not <= 1
TabFileException - error caused by incorrect input tab file
TabConfigurationException - exception caused by incorrect program configuration file
StaffException - caused by illegal StaffString object construction
StaffOutOfBoundsException - caused by accessing a StaffString index that is out of bounds
LoggingError - caused by inability to open log file.

Some of these exceptions are used in try-except clauses that handle a more generic Python exception (e.g. ValueError, IOError) and then raise one of these exception types
to better inform the user.

author: Chami Lamelas
date: Summer 2019
"""

class TabException(Exception):
    def __init__(self, msg):
        self.msg = msg
    def __str__(self):
        return str(self.msg)

class MeasureException(TabException):
    def __init__(self, op, reason):
        super().__init__("Operation on Measure failed: {0}. Reason: {1}.".format(op, reason))

class TabFileException(TabException):
    def __init__(self, count):
        super().__init__("Invalid line count. {0} lines were interpreted as either timing information lines or strings.".format(count))

class TabConfigurationException(TabException):
    DEFAULT_CONFIG_LINK = ""

    # first line in the file is line 1.
    def __init__(self, reason="not specified", line=0):
        super().__init__("Program configuration failed. Error on line {0}. Reason: {1}. If you cannot solve the problem, please utilize the default configuration file located at {2}.".format(line, reason, TabConfigurationException.DEFAULT_CONFIG_LINK))

class StaffException(TabException):
    def __init__(self, op, reason, str):
        super().__init__("Staff operation cannot be performed: {0}, Reason: {1}. str={2}".format(op, reason, str))

class StaffOutOfBoundsException(TabException):
    def __init__(self, reason, viol):
        super().__init__("Bounds Violation, reason: {0} ({1})".format(reason, viol))

class LoggingException(Exception):
    def __init__(self, op, reason):
        self.msg = "Log operation \"{0}\" failed. Reason: {1}".format(op, reason)
    def __str__(self):
        return str(self.msg)
