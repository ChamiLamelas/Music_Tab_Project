"""
This file provides a logging utility to tabReader.py. That way, the user sees output in an organized log file as opposed to the console. However, if an error occurs in the logging
process, the issue is still printed to the console. The file has 1 class, Logger.

author: Chami Lamelas
date: Summer 2019
"""

from datetime import datetime
from exceptionsLibrary import LoggingException
import getpass
import platform
import os

"""
This class provides the logging ability described above in the file description. The class has 2 attributes:

logFile - a file object that will remain open until closed by close() or by the garbage collector
newSession - truth value indicating if the user has started a new logging session. It becomes True once open() is called and False after the first call to log(). That is, when
something is actually logged by the user.

Logger also has several static variables: the latter 4 are logging "types"; they are displayed at the beginning of a logged message and can illustrate the importance/meaning of
a logged message. The user can provide different ones by changing the "type" parameter of the log() method below.

LOG_FILENAME - the name of the log file for this program. For the purpose of causing the least confusion to the user, it is not variable.
ERROR - the error logging type, most visible of the default logging types; use when reporting exceptions
INFO - the info logging type, least visible of the default logging types; use when reporting non-essential info to the user
WARNING - the warning logging type, somewhat visible; use when the user should be warned
LOG - the log logging type, somewhat visible; use when the Logger class should be reporting something to the user
"""
class Logger:
    LOG_FILENAME = "tabReaderLOG.log"
    ERROR = ">> ERROR >>"
    INFO = "Info"
    WARNING = "> Warning >"
    LOG = "> Log >"

    """
    Constructs an empty Logger. Use open() before beginning to log any messages.
    """
    def __init__(self):
        self.logFile = None
        self.newSession = False

    """
    Opens the log file for future logging purposes and marks the beginning of a new logging session.

    Raises LoggingException if the log file cannot be opened properly.
    """
    def open(self):
        try: # try to open the log file and mark a new session being started if opening was successful. Wrap any IOError that occurs as a LoggingException.
            self.logFile = open(Logger.LOG_FILENAME,"a+")
            self.newSession = True
        except IOError as i:
            raise LoggingException("opening", "log file (" + Logger.LOG_FILENAME + ") could not be opened. " + str(i))

    """
    Logs a message of a certain type to the log file. If this fails, a LoggingException is thrown (see below) and the Logger is automatically closed.

    params:
    msg - a message to log
    type - the type of the message being logged. The default types and the idea of a type are explained in the class doc.

    Raises LoggingException if the log file hasn't been opened, is already closed, or the message cannot be written.
    """
    def log(self, msg, type=INFO):
        if self.logFile is None:
            raise LoggingException("logging", "log file (" + Logger.LOG_FILENAME + ") has not been opened. Use open().")
        if self.logFile.closed:
            raise LoggingException("logging", "log file (" + Logger.LOG_FILENAME + ") has been closed. Re-open using open().")
        try: # try to log to the log file and wrap any IOError that occurs as a LoggingException
            time = str(datetime.now()) # mark date & time of log
            if self.newSession: # if this is the beginning of a new session, log that and mark the session is no longer new.
                self.logFile.write("\n[{0}][{1}] New Log Session started with the following platform information:\n".format(time, Logger.LOG))
                osInfo = platform.system() + " " + platform.version()
                srcPath = os.path.dirname(os.path.realpath(__file__))
                self.logFile.write("[{0}][{1}] User: {2}. Python version: {3}. OS Info.: {4}. Source directory: {5}.\n".format(time, Logger.LOG, getpass.getuser(), platform.python_version(), osInfo, srcPath))
                self.newSession = False
            self.logFile.write("[{0}][{1}] {2}\n".format(time, type, msg)) # log the actual message with the provided type.
        except IOError as i:
            self.close() # if an error has occurred, close log file to avoid resource leak
            raise LoggingException("logging", "I/O Error when trying to write to log file after it was opened ("+ Logger.LOG_FILENAME +"): " + str(i))

    """
    Closes the log file to avoid a resource leak. This should always be called once you are done using the Logger to not wait for the garbage collector to do this for you.

    Raises LoggingException if log file was never opened.
    """
    def close(self):
        if self.logFile is None:
            raise LoggingException("closing", "log file ("+ Logger.LOG_FILENAME +") was never opened.")
        self.newSession = False # in case log() was never called, mark session ended anyway
        self.logFile.close()
