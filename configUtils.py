"""
This file provides the ability through the ConfigReader class to read the configuration file used by tabReader.py and generate the default configuration file if needed.
Note: you can add comments throughout the config file by starting every comment line with a hashtag "#" as with Python. Comments can also be added at the end of config lines. Any characters after the "#" in a comment line will be ignored

author: Chami Lamelas
date: Summer 2019
"""

from exceptionsLibrary import TabConfigurationException
from pathlib import Path
"""
This class is used to read the configuration file to be used by tabReader.py. The class has only 1 attribute:

lines - a list of Strings that holds non-empty lines of the configuration file stripped of whitespace

In addition, the class has several static variables used in identifying components of the configuration file:

CONFIG_FILENAME - the name of the config. file (for the purpose of making things easier for the user, it is not variable)
SETTING_YES - signifies that a given config option should apply for this run of the program
SETTING_NO - signifies the opposite of aforementioned
TIMING_SUPPLIED_ID - id of the option that signifes timing is supplied (that is there is a line above the strings with W's, H's, Q's. etc.)
"""
class ConfigReader:

    CONFIG_FILENAME = "tabReader.config"
    SETTING_YES = "true"
    SETTING_NO = "false"
    TIMING_SUPPLIED_ID = "timingsupplied"
    GAPSIZE_ID = "gapsize"
    COMMENT = "#"

    """
    Constructs an empty ConfigReader. Use readConfigFile() to load the configuration file into this object.
    """
    def __init__(self):
        self.lines = list()

    """
    Returns True if the OS can find a path to the config file, False if not.
    """
    def configFileFound():
        return Path(ConfigReader.CONFIG_FILENAME).is_file()

    """
    Checks if the config file has been loaded into this object so methods that retrieve config data can function properly.

    Raises TabConfigurationException if no data has been read from the config file.
    """
    def checkConfigFileLoaded(self):
        if not self.lines:
            raise TabConfigurationException(reason="config file not loaded properly. Use readConfigFile() to try again or reset to the default config file by calling ConfigReader.buildDefaultConfigFile().")

    """
    If the config file can be found, loads the files contents into self.lines. Otherwise, this method builds the configuration file and then re-runs the program.
    Infinite recursion is prevented by only trying to build the default configuration file again once. If that cannot be done (signified by a raised
    TabConfigurationException - see buildDefaultConfigFile() doc.), method just exits.

    Returns whether or not the config file was found. Thus, True indicates a config file could be found and was loaded. False indicates the default file was built and read.

    raises TabConfigurationException if there was an I/O error opening config file or if buildDefaultConfigFile() fails.
    """
    def readConfigFile(self):
        if ConfigReader.configFileFound():
            try: # since a config file has been found, try to read it. Ignore lines marked as comments or that are empty. Wrap any IOErrors as TabConfigurationExceptions.
                with open(ConfigReader.CONFIG_FILENAME) as configFile:
                    for line in configFile:
                        if not line.startswith(ConfigReader.COMMENT):
                            sLine = "".join(line.split()) # remove any separating whitespace
                            if len(sLine) > 0:
                                # strip off any end of line comments
                                idx = sLine.find(ConfigReader.COMMENT)
                                if (idx > 0):
                                    sLine = sLine[:-(len(sLine)-idx)]
                                self.lines.append(sLine)
                return True
            except IOError as i:
                raise TabConfigurationException(reason="I/O error opening config. file: " + i)
        else: # since a config file could not be found, build the default one and call this method again.
            ConfigReader.buildDefaultConfigFile()
            self.readConfigFile()
            return False

    """
    Returns the setting for an option specified by the user in the config file. The option is identified by 2 parameters:

    params:
    lineNum - the number of the non-empty line the option should appear on
    id - the option's ID

    Raises TabConfigurationException if checkConfigFileLoaded() failed, the ID at lineNum didn't match the id param., or there was no "=" in the line.
    """
    def getSetting(self, lineNum, id):
        self.checkConfigFileLoaded()
        if not self.lines[lineNum].startswith(id): # option's setting line must start with option's id
            raise TabConfigurationException(reason="improper ID. Must be {0}.".format(id), line=lineNum)
        idx = self.lines[lineNum].find("=")
        if idx != len(id): # option id and setting must be separated by an "="
            raise TabConfigurationException(reason="missing \"=\".", line=lineNum)
        return self.lines[lineNum][idx+1:] # setting is whatever follows the "="

    """
    Returns True if the user specified that timing has been supplied and False if the user specified the opposite

    Raises TabConfigurationException if getSetting() failed on the config file for the timing supplied option or if the setting found in the config file for this option could not
    be recognized.
    """
    def getTiming(self):
        setting = self.getSetting(0, ConfigReader.TIMING_SUPPLIED_ID) # timing supplied option must be on line 0
        if setting == ConfigReader.SETTING_YES:
            return True
        elif setting == ConfigReader.SETTING_NO:
            return False
        else: # only 2 allowed settings are True or False
            raise TabConfigurationException(reason="setting {0} not recognized. Must be {1} or {2}".format(setting, ConfigReader.SETTING_YES, ConfigReader.SETTING_NO), line=1)

    """
    Returns the gapsize to be placed between Slices in the resulting Song generated by tabReader.py.

    Raises TabConfigurationException if getSetting() failed on the config file for the gapsize option or if the setting found in the config file was not a non-negative integer
    """
    def getGapsize(self):
        setting = self.getSetting(1, ConfigReader.GAPSIZE_ID) # gapsize option must be on line 1
        try:
            gapSize = int(setting)
            if gapSize < 0:
                raise ValueError()
        # 2 sources of ValueErrors in try-statement: (1) setting is not an int, raised by int(). (2) ValueError manually raised by gapSize < 0. One is manually raised because both
        # possible problems with the gapSize both fall under a "value" problem. These can be easily grouped into the same error message.
        except ValueError:
            raise TabConfigurationException(reason="setting {0} not recognized. Must be a non-negative integer.".format(setting), line=2)
        return gapSize

    """
    Builds the default config file. WARNING: calling this method will overwrite any pre-existing file with the same path as this program's config file.

    Raises TabConfigurationException if the file could not be created
    """
    def buildDefaultConfigFile():
        DEFAULT_TIMING_SUPPLIED = ConfigReader.SETTING_NO
        DEFAULT_GAPSIZE = 3

        defaultConfig = "# This is the configuration file for the tab reader program. \n# You can leave comments throughout this file by starting each comment line with a hashtag, like with Python.\n"+ConfigReader.TIMING_SUPPLIED_ID+"="+DEFAULT_TIMING_SUPPLIED+"\n"+ConfigReader.GAPSIZE_ID+"="+str(DEFAULT_GAPSIZE)

        try: # try to write the default configuration to the config file, wrap any IOError that occurs as a TabConfigurationException
            with open(ConfigReader.CONFIG_FILENAME, "w+") as configFile:
                configFile.write(defaultConfig)
        except IOError as i:
            raise TabConfigurationException(reason="configuration file could not be created; an I/O Error occurred: " + str(i))
