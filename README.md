# Music Tab Project

The primary purpose of this project was to provide a program that takes a text file holding a bass guitar tab and converting it into an HTML file that holds a tablature or bass clef representation of the same notes.

**Date:** Summer 2019

## Getting Started

This section will inform you of the necessary prerequisites to run this program, the necessary files, and how to prepare program input files.

### Prerequisites

First, you need to install Python. This program was written and tested using *Python 3.7.2*. To download Python you can go [here](https://www.python.org/downloads/). Make sure that Python has been added to the system path.
Second, the program's output was tested in [Mozilla Firefox](https://www.mozilla.org/en-US/firefox/new/) and [Google Chrome](https://www.google.com/chrome/) on Windows Version 10.0.17763.503. So, it may be best to download one of those browsers. Their download links are embedded in their names.

### Installing

Each of the Python source files in the repository is necessary for the program to perform its intended purpose. To see what each one does, read the documentation at the top of each file. If you are interested, you can also read the documentation of each class and method in the source files.

You can download the configuration file if you wish, if you run the program it will automatically generate one if it doesn't locate one on your computer.

Make sure that *every* file you download is put in the *same* folder.

### Preparing an Input Tab File

The input tab files follow the general format of tabs found on [Ultimate Guitar Tabs](https://www.ultimate-guitar.com/). Here are some rules on how you should be structuring your input files:

**(1)** Lines that are meant to be strings must be only made up of *ONLY* the following characters *AND* must end with a vertical bar:

* newline/carriage return: "\n"
* tab: "\t"
* *only* the uppercase letters that belong to the set of bass string ids {G, D, A, E}
* vertical bar: "|"
* hyphen: "-"
* space: " "
* digits (0-9)

**(2)** Lines that are meant to list the timings of notes that are played must be made up of *ONLY* the following characters:

* newline/carriage return: "\n"
* tab: "\t"
* tie marking: "+"
* dot marking: "."
* space: " "
* *only* the uppercase letters that belong to the timing IDs {W, H, Q, E, S}

These lines should only be present if the timing is supplied in the tab, which is usually not the case. Make sure that if the timing is supplied, the 1st configuration line (not counting empty lines or comments) should be

```
timingsupplied=true
```

**Note:** This means that other lines that are made up of only characters matching one of these 2 sets will be interpreted by the program as a string or timing line and could lead to an error. For example, if you are writing notes as in the case of this sample file and have a bar line made of hyphens, this would lead to an error in the file reading:

```
Duration Legend

---------------

W - whole; H - half; Q - quarter; E - 8th; S - 16th; T - 32nd; X - 64th; a - acciaccatura
```

**(3)** The timing letter ID that signifies the length of a note is assumed to be located above the first digit of the fret that the note corresponds to. For example, if note on the E-string 10th fret (D) is meant to be a quarter note, the portion of the input tab that corresponds to this should appear as so:

```
   Q
G|----|
D|----|
A|----|
E|-10-|
```

The following would lead to an error:

```
    Q
G|----|
D|----|
A|----|
E|-10-|
```

**(4)** 2 notes should not overlap in such a way their fret numbers are not fully on top of each other. For example, the following would be a violation because 10 and 11 overlap. the note on the d-string would not be read properly

```
     QQ
G|---10---|
D|----11--|
A|--------|
E|--------|
```

**Note:** You can have chords in the where notes with the same timing are stacked like so in the case of a C power chord to be played for a half note:

```
   W
G|----|
D|----|
A|-10-|
E|-8--|
```

**Warning:** Not every possible problem with an input tab file is listed above. The error reporting system outlined in the exceptions library is meant to assist in helping prepare a correct input tab file.

## Running the Program

Once you have installed the required files and have a tab file, say located at "C:\\Users\\Chami\\Desktop\\test_tab.txt", open your operating system's command line. First, navigate to the directory where you have installed the source files and run the following command:

```
py tabReader.py C:\\Users\\Chami\\Desktop\\test_tab.txt
```

After the first time you run the program, a log file will be generated and placed in the same folder. You can ignore the log file, it is meant to provide a more organized way of displaying the operation of the program. All program output will be put here unless logging itself fails. In this case, check the console you ran the program in.

### Using the Configuration File

The configuration file is designed to provide the user more freedom in how the program runs. It may be best to examine the default configuration file before writing one on your own. And make sure it has the same name as the default configuration file. Furthermore, to help yourself, you can add line comments in the configuration file by placing a hashtag "#" at the beginning of each comment line (as with Python). Errors in the configuration file are also reported to the log file.

**Important:** If you wish write your own configuration file and provide different settings for the various options that can be configured in this program, make sure you put the new options and settings in the same order as in the default configuration file. Otherwise, an error will occur. 

### Note about Cygwin

If you are interested in using Cygwin to run the program, I encountered an error with the time logging when I used Cygwin. After some research I found it could have been caused by Cygwin updating the Windows time zone environmental variable in such a way that Windows failed to interpret it correctly and switched to a default time zone (which seemed to be 1 hour after Greenwich Mean Time (GMT)). I wasn't confident about editing system environmental variables, which can be done through Cygwin, so I decided it was best to use Windows Command Prompt.

## Future Development

If interested, here are possible major additions to later versions of the project:

* Support for non-standard tuning (G, D, A, E).
* A version for instruments other than a 4-string bass.
* Support for other timing identifiers than W, H, Q, E, and S for whole note, half note, quarter note, eighth note, and sixteenth note respectively.

## Built With

* [Python 3.7.2](https://www.python.org/downloads/) - Python version. View the list of versions on the website.
* [Atom](https://atom.io/) - IDE I used for development.

## Authors

* **Chami Lamelas** - *Developer* - [LiquidsShadow](https://github.com/LiquidsShadow)

## Acknowledgments

* [PurpleBooth](https://github.com/PurpleBooth) - wrote the template for this file
