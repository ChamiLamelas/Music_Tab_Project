"""
This file provides the ability through the ConfigReader class to read the configuration file used by tabReader.py and generate the default configuration file if needed.
Note: you can add comments throughout the config file by starting every comment line with a hashtag "#" as with Python. Comments can also be added at the end of config lines. Any characters after the "#" in a comment line will be ignored

author: Chami Lamelas
date: Summer 2019
"""

from exceptionsLibrary import TabConfigurationException
from pathlib import Path
from enum import Enum

"""
Enum that

TIMING_SUPPLIED - line number and id of 'hasTiming' attribute in ConfigReader
GAPSIZE - line number and id of 'gapsize' attribute in ConfigReader
TAB_SPACING - line number and id of 'tabSpacing' attribute in ConfigReader
HAS_EXTRA - line number and id of 'hasExtra' attribute in ConfigReader
PLAYING_LEGEND - line number and id of 'playingLegend' attribute in ConfigReader
"""
class ConfigOptionID(Enum):
      TIMING_SUPPLIED = 0
      GAPSIZE = 1
      TAB_SPACING = 2
      HAS_EXTRA = 3
      PLAYING_LEGEND = 4
      TIE_SYMBOL = 5
      DOT_SYMBOL = 6

"""
This class is used to read the configuration file to be used by tabReader.py. The class stores the config. options' settings as attributes in addition to the list of lines read from the input config. file:

lines - a list of Strings that holds non-empty lines of the configuration file stripped of whitespace
hasTiming - the option that signifes timing is supplied (that is there is a line above the strings with W's, H's, Q's. etc.)
gapsize - the option that signfies the output's sheet music gapsize (see Song doc. in typeLibrary.py)
tabSpacing - the option that signifies the number of spaces in a tab in the user's text editor
hasExtra - the option that signifies whether extra text exists in the file
playingLegend - the option that holds a legend of other characters that may appear in string lines (e.g. h for hammer-ons, p for pull-offs, b for bends, etc.)

WARNING: It is not advised to access the attributes/instance fields regarding the config. options directly. This is because there is no guarantee that they have actually been read by the reading methods
discussed below. Therefore, it is best to use the their respective accessor/getter methods listed at the end of the class. These will check that they have actually been read and provide more appropriate
output. To avoid repeatedly doing the checks in client code that doesn't change the configuration, store the output of the getter methods in temp./local variables. If you wish to access the instance fields
directly, it is advised to use the read-check (exist) methods before. These are listed alongside the accessor/getter methods at the end of the class.

In addition, the class has several static variables used in identifying components of the configuration file:

CONFIG_FILENAME - the name of the config. file (for the purpose of making things easier for the user, it is not variable)
COMMENT - the character that signifies the beginning of a line comment in the config. file
SETTING_YES - signifies that a given config option should apply for this run of the program
SETTING_NO - signifies the opposite of aforementioned
defaultConfig - the text to be placed in the default config. file by 'buildDefaultConfigFile()'. Loaded on file import.
"""
class ConfigReader:

    CONFIG_FILENAME = "tabReader.config"
    COMMENT = "#"
    SETTING_YES = "true"
    SETTING_NO = "false"
    defaultConfig = ""

    """
    Constructs an empty ConfigReader. Use readConfigFile() to load the configuration file into this object.
    """
    def __init__(self):
        self.lines = list()
        self.hasTiming = -1
        self.gapsize = -1
        self.tabSpacing = -1
        self.hasExtra = -1
        self.playingLegend = None
        self.tieSymbol = ""
        self.dotSymbol = ""

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
    def open(self):
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
                        # else: full line is a comment, ignore
                return True
            except IOError as i:
                raise TabConfigurationException(reason="I/O error opening config. file: " + i)
        else: # since a config file could not be found, build the default one and call this method again.
            ConfigReader.buildDefaultConfigFile()
            self.open()
            return False

    """
    Reads all the options and loads them into the ConfigReader attributes.

    Raises TabConfigurationException if any of the reading methods failed.
    """
    def readAllOptions(self):
        self.readTiming()
        self.readGapsize()
        self.readTabSpacing()
        self.readHasExtra()
        self.readPlayingLegend()
        self.readTieSymbol()
        self.readDotSymbol()

    """
    Reads the setting for an option specified by the user in the config file.

    params:
    option - a ConfigOptionID that identifies the config. option

    Raises TabConfigurationException if checkConfigFileLoaded() failed, the config. file is too small and the option cannot be found, the option id in the file was wrong, or there was no "=" in the option line
    """
    def readSetting(self, option: ConfigOptionID):
        self.checkConfigFileLoaded()
        if option.value >= len(self.lines):
            raise TabConfigurationException(reason="config. file too small")
        if not self.lines[option.value].startswith(option.name): # option's setting line must start with option's id
            raise TabConfigurationException(reason="improper ID. Must be {0}.".format(option.name), line=option.value)
        idx = self.lines[option.value].find("=")
        if idx != len(option.name): # option id and setting must be separated by an "="
            raise TabConfigurationException(reason="missing \"=\".", line=option.value)
        return self.lines[option.value][idx+1:] # setting is whatever follows the "="

    """
    Reads the True/False setting for the timing supplied option.

    Raises TabConfigurationException if getSetting() failed on the config file for the timing supplied option or if the setting found in the config file for this option could not
    be recognized.
    """
    def readTiming(self):
        setting = self.readSetting(ConfigOptionID.TIMING_SUPPLIED)
        if setting == ConfigReader.SETTING_YES:
            self.hasTiming = 1
        elif setting == ConfigReader.SETTING_NO:
            self.hasTiming = 0
        else: # only 2 allowed settings are True or False
            raise TabConfigurationException(reason="setting {0} not recognized. Must be {1} or {2}".format(setting, ConfigReader.SETTING_YES, ConfigReader.SETTING_NO), line=ConfigOption.TIMING_SUPPLIED.value+1)

    """
    Reads the integer gapsize to be placed between Slices in the resulting Song generated by tabReader.py.

    Raises TabConfigurationException if getSetting() failed on the config file for the gapsize option or if the setting found in the config file was not a non-negative integer
    """
    def readGapsize(self):
        setting = self.readSetting(ConfigOptionID.GAPSIZE)
        try:
            nSetting = int(setting)
            if nSetting < 0:
                raise ValueError()
        # 2 sources of ValueErrors in try-statement: (1) setting is not an int, raised by int(). (2) ValueError manually raised by gapSize < 0. One is manually raised because both
        # possible problems with the gapSize both fall under a "value" problem. These can be easily grouped into the same error message.
        except ValueError:
            raise TabConfigurationException(reason="setting \"{0}\" not recognized. Must be a non-negative integer.".format(setting), line=ConfigOption.GAPSIZE.value+1)
        else:
            self.gapsize = nSetting

    """
    Reads the integer tab spacing of the editor used to create the input text file. By default the spacing is 8, but modern text editors allow for the number of spaces in a tab character to be reduced.
    This provides a way for the user to specify that.

    Raises TabConfigurationException if getSetting() failed on the config file for the tab spacing option or if the setting found in the config file was not a non-negative integer
    """
    def readTabSpacing(self):
        setting = self.readSetting(ConfigOptionID.TAB_SPACING)
        try:
            nSetting = int(setting)
            if nSetting < 0:
                raise ValueError()
        except ValueError: # see note on ValueError handling in getGapsize() above
            raise TabConfigurationException(reason="setting \"{0}\" not recognized. Must be a non-negative integer.".format(setting), line=ConfigOptionID.TAB_SPACING.value+1)
        else:
            self.tabSpacing = nSetting

    """
    Reads True/False value of whether user has specified that the input text file has extra text. That is, notes or identifications of verses, etc. If the user removes all extra text that is all
    non string and timing lines from the input file, the performance of loadLinesIntoLists() in tabReader.py increases.

    Raises TabConfigurationException if getSetting() failed on the config file for the has extra option or if the setting found in the config file could not be recognized.
    """
    def readHasExtra(self):
        setting = self.readSetting(ConfigOptionID.HAS_EXTRA)
        if setting == ConfigReader.SETTING_YES:
            self.hasExtra = 1
        elif setting == ConfigReader.SETTING_NO:
            self.hasExtra = 0
        else: # only 2 allowed settings are True or False
            raise TabConfigurationException(reason="setting \"{0}\" not recognized. Must be {1} or {2}".format(setting, ConfigReader.SETTING_YES, ConfigReader.SETTING_NO), line=ConfigOptionID.HAS_EXTRA.value+1)

    """
    Reads the legend as described in the ConfigReader attributes doc. as a set of characters.

    Raises TabConfigurationException if getSetting() failed on the config file for the legend option or if the legend contains a whitespace character or digit (0-9).
    """
    def readPlayingLegend(self):
        setting = self.readSetting(ConfigOptionID.PLAYING_LEGEND) # legend option must be on line 4
        leg = set()
        for ch in setting:
            if ch.isdigit() or ch.isspace():
                raise TabConfigurationException(reason="illegal legend value \"{0}\". Cannot be a whitespace character or digit (0-9)".format(ch), line=ConfigOptionID.PLAYING_LEGEND.value+1)
            else:
                leg.add(ch)
        self.playingLegend = leg

    """
    Reads the tie symbol config. option.

    Raises TabConfigurationException if getSetting() fails or the tie symbol setting is not a single character.
    """
    def readTieSymbol(self):
        setting = self.readSetting(ConfigOptionID.TIE_SYMBOL)
        if len(setting) != 1:
            raise TabConfigurationException(reason="setting \"{0}\" not recognized. Must be a single character.".format(setting), line=ConfigOptionID.TIE_SYMBOL.value+1)
        self.tieSymbol = setting

    """
    Reads the dot symbol config. option.

    Raises TabConfigurationException if getSetting() fails or the dot symbol setting is not a single character.
    """
    def readDotSymbol(self):
        setting = self.readSetting(ConfigOptionID.DOT_SYMBOL)
        if len(setting) != 1:
            raise TabConfigurationException(reason="setting \"{0}\" not recognized. Must be a single character.".format(setting), line=ConfigOptionID.DOT_SYMBOL.value+1)
        self.dotSymbol = setting

    """
    Builds the default config file. WARNING: calling this method will overwrite any pre-existing file with the same path as this program's config file.

    Raises TabConfigurationException if the file could not be created
    """
    def buildDefaultConfigFile():
        try: # try to write the default configuration to the config file, wrap any IOError that occurs as a TabConfigurationException
            with open(ConfigReader.CONFIG_FILENAME, "w+") as configFile:
                configFile.write(ConfigReader.defaultConfig)
        except IOError as i:
            raise TabConfigurationException(reason="configuration file could not be created; an I/O Error occurred: " + str(i))

    """
    Reports that an option reading has failed by raising a TabConfigurationException.

    params:
    option - the ConfigOption for which the reading failed

    Raises TabConfigurationException as explained above.
    """
    def reportOptionReadFailure(option: ConfigOptionID):
        raise TabConfigurationException(reason="configuration option \"{0}\" has not been read. Please use 'readAllOptions()' or another reading method.".format(option.name), line=option)

    """
    Returns whether or not a timing setting was read successfully.
    """
    def timingExists(self):
        return self.hasTiming != -1

    """
    Checks that the timing supplied option has been read before returning its value to the user. Use instead of directly accessing 'self.hasTiming' for more suitable output.

    Raises TabConfigurationException if 'timingExists()' returns False
    """
    def isTimingSupplied(self):
        if not self.timingExists():
            ConfigReader.reportOptionReadFailure(ConfigOptionID.TIMING_SUPPLIED)
        return self.hasTiming == 1

    """
    Returns whether or not a gapsize setting was read successfully.
    """
    def gapsizeExists(self):
        return self.gapsize != -1

    """
    Checks that the gapsize option has been read before returning its value to the user. Use instead of directly accessing 'self.gapsize'.

    Raises TabConfigurationException if 'gapsizeExists()' returns False
    """
    def getGapsize(self):
        if not self.gapsizeExists():
            ConfigReader.reportOptionReadFailure(ConfigOptionID.GAPSIZE)
        return self.gapsize

    """
    Returns whether or not a tab spacing setting was read successfully.
    """
    def tabSpacingExists(self):
        return self.tabSpacing != -1

    """
    Checks that the tab spacing option has been read before returning its value to the user. Use instead of directly accessing 'self.tabSpacing'.

    Raises TabConfigurationException if 'tabSpacingExists()' returns False
    """
    def getTabSpacing(self):
        if not self.tabSpacingExists():
            ConfigReader.reportOptionReadFailure(ConfigOptionID.TAB_SPACING)
        return self.tabSpacing

    """
    Returns whether or not an extra text setting was read successfully.
    """
    def extraTextExists(self):
        return self.hasExtra != -1

    """
    Checks that the extra text present option has been read before returning its value to the user. Use instead of directly accessing 'self.hasExtra'.

    Raises TabConfigurationException if 'extraTextExists()' returns False
    """
    def isExtraTextPresent(self):
        if not self.extraTextExists():
            ConfigReader.reportOptionReadFailure(ConfigOptionID.HAS_EXTRA)
        return self.hasExtra == 1

    """
    Returns whether or not a playing legend was read successfully.
    """
    def playingLegendExists(self):
        return self.playingLegend != None

    """
    Checks that the playing legend has been read before returning its value to the user. Use instead of directly accessing 'self.playingLegend'.

    Raises TabConfigurationException if 'playingLegendExists()' returns False
    """
    def getPlayingLegend(self):
        if not self.playingLegendExists():
            ConfigReader.reportOptionReadFailure(ConfigOptionID.PLAYING_LEGEND)
        return self.playingLegend

    """
    Returns whether or not a tie symbol option was read successfully.
    """
    def tieSymbolExists(self):
        return self.tieSymbol != ""

    """
    Checks that the tie symbol option has been read before returning its value to the user. Use instead of directly accessing 'self.tieSymbol'.

    Raises TabConfigurationException if 'tieSymbolExists()' returns False
    """
    def getTieSymbol(self):
        if not self.tieSymbolExists():
            ConfigReader.reportOptionReadFailure(ConfigOptionID.TIE_SYMBOL)
        return self.tieSymbol

    """
    Returns whether or not a dot symbol option was read successfully.
    """
    def dotSymbolExists(self):
        return self.dotSymbol != ""

    """
    Checks that the dot symbol option has been read before returning its value to the user. Use instead of directly accessing 'self.dotSymbol'.

    Raises TabConfigurationException if 'dotSymbolExists()' returns False
    """
    def getDotSymbol(self):
        if not self.dotSymbolExists():
            ConfigReader.reportOptionReadFailure(ConfigOptionID.DOT_SYMBOL)
        return self.dotSymbol

"""
Script to load default config. file text ('ConfigReader.defaultConfig')
"""
defaultValues = list() # create an empty list to hold default values
for i in range(0, len(ConfigOptionID)):
    defaultValues.append(None)

# associate with each config. option a default value by placing it in the index equal to the value of the ConfigOptionID corresponding to it
defaultValues[ConfigOptionID.TIMING_SUPPLIED.value] = ConfigReader.SETTING_NO
defaultValues[ConfigOptionID.GAPSIZE.value] = 3
defaultValues[ConfigOptionID.TAB_SPACING.value] = 8
defaultValues[ConfigOptionID.HAS_EXTRA.value] = ConfigReader.SETTING_YES
defaultValues[ConfigOptionID.PLAYING_LEGEND.value] = ""
defaultValues[ConfigOptionID.TIE_SYMBOL.value] = "+"
defaultValues[ConfigOptionID.DOT_SYMBOL.value] = "-"

# place it into the default file text static variable
ConfigReader.defaultConfig = "# This is the configuration file for the tab reader program. \n# You can add line comments in the configuration file similarly to how it is done in Python: \n# (1) Placing a hashtag \"#\" at the beginning of each comment line. \n# (2) Placing a \"#\" at the end of configuration lines. The program will ignore any text following the hashtag."
for id in ConfigOptionID:
    ConfigReader.defaultConfig += "\n" + id.name + "=" + str(defaultValues[id.value])
