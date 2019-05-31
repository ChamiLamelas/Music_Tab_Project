# Music Tab Project

The primary purpose of this project was to provide a program that takes a text file holding a bass guitar tab and converting it into sheet music displayed in an HTML file.

**Date:** Summer 2019

## Getting Started

This section will inform you of the necessary prerequisites to run this program, the necessary files, and how to prepare program input files.

**Note:** the installation and running of this program has *NOT*  been tested on OSX.

### Prerequisites

First, you need to install a version of Python **3**. Python 2.x is *NOT* supported. This program was written and tested using *Python 3.7.2*. To download Python you can go [here](https://www.python.org/downloads/). Make sure that Python has been added to the system path.
Second, the program's output was tested in [Mozilla Firefox 67.0 (64-bit)](https://www.mozilla.org/en-US/firefox/new/) and [Google Chrome Version 74.0.3729.169 (Official Build) (64-bit)](https://www.google.com/chrome/) on Windows Version 10.0.17763.503. So, it may be best to download one of those browsers. Their download links are embedded in their names.

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

**(2)** lines that are meant to be strings must start with G, D, A, or E, followed by a "|", followed by a sequence of *ONLY* the following characters, end with a "|", and must be at least 4 characters long.

newline/carriage return: "\n"
tab: ""\t"
vertical bar: "|"
hyphen: "-"
space: " "
digits (0-9)

These lines should only be present if the timing is supplied in the tab, which is usually not the case. Make sure that if the timing is supplied, the 1st configuration line (not counting empty lines or comments) should be

```
timingsupplied=true
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

**(4)** 2 notes should not overlap in such a way their fret numbers are not fully on top of each other. For example, the following would be a violation because 10 and 11 overlap. the note on the D-string would not be read properly

```
     QQ
G|---10---|
D|----11--|
A|--------|
E|--------|
```

**Note:** You can have chords where notes with the same timing are stacked like so in the case of a C power chord to be played for a half note:

```
   H
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

After you run the program, an output HTML file encoded in *UTF-8* will be generated, in this case it will have the path "C:\\Users\\Chami\\Desktop\\test_tab_staff.html". To view this file, open it using a browser than can display the Unicode characters that are included such as [Mozilla Firefox 67.0 (64-bit)](https://www.mozilla.org/en-US/firefox/new/) or [Google Chrome Version 74.0.3729.169 (Official Build) (64-bit)](https://www.google.com/chrome/).

**Note:** If you run the same command again, the contents of this file will be overwritten, so if you wish to save the first output, I would rename the file or move it to another directory.

### The Log File

After the first time you run the program, a log file will be generated and placed in the same folder. All program output will be placed into this file unless the logging itself fails. This includes any errors that are reported, so this file should be checked to make sure your program ran successfully. It is meant to be a more organized display of program output than simply printing to the console program you ran the program from.

**Note:** If a logging error occurs, that will be printed to the console.

### Using the Configuration File

The configuration file is designed to provide the user more freedom in how the program runs. It may be best to examine the default configuration file before writing one on your own. And make sure it has the same name as the default configuration file. Furthermore, to help yourself, you can add line comments in the configuration file by placing a hashtag "#" at the beginning of each comment line (as with Python). Comments can also be made after configuration lines by placing a "#". The program will ignore any text following the hashtag. Lastly, errors in the configuration file are also reported to the log file.

**Important:** If you wish to write your own configuration file and provide different settings for the various options that can be configured in this program, make sure you put the new options and settings in the same order as in the default configuration file. Otherwise, an error will occur.

### Note about Cygwin

If you are interested in using Cygwin to run the program, I encountered an error with the time logging when I used Cygwin. After some research I found it could have been caused by Cygwin updating the Windows time zone environmental variable in such a way that Windows failed to interpret it correctly and switched to a default time zone (which seemed to be 1 hour after Greenwich Mean Time (GMT)). I wasn't confident about editing system environmental variables, which can be done through Cygwin, so I decided it was best to use Windows Command Prompt.

### Output and HTML

The reason that the staff output is displayed in an HTML file as opposed to an ASCII text file is to allow the display of the musical symbols which are Unicode characters whose codes can be found in this [PDF](https://unicode.org/charts/PDF/U1D100.pdf). Furthermore, the installation of either [Mozilla Firefox 67.0](https://www.mozilla.org/en-US/firefox/new/) or [Google Chrome](https://www.google.com/chrome/) was recommended because they were able to display these Unicode characters while Microsoft Edge could not.

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
