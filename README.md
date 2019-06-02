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

**(1)** Lines that are meant to be strings must satisfy the following 5 properties.

*(i)* Any whitespace must be at either the front or rear of the line, **none** in between measures or notes.  
*(ii)* The first non-whitespace character must be G, D, A, or E followed by a "|" or just be "|".  
*(iii)* Following either case of *(ii)*, a sequence of *ONLY* the following characters:  

* vertical bar: "|"
* hyphen: "-"
* digits (0-9)

*(iv)* The last non-whitespace character must be a "|".  
*(v)* Be at least 4 characters long, not counting the whitespace at either end.

**(2)** Lines that are meant to list the timings of notes that are played must be made up of *ONLY* the following characters and must contain at least **1** non-whitespace character.

* newline/carriage return: "\n" (at the end)
* tab: "\t"
* tie marking: "+"
* dot marking: "."
* space: " "
* *only* the uppercase letters that denote lengths of time: W, H, Q, E, and S

These lines should *only* be present if the timing is supplied in the tab, which is usually not the case. Make sure that if the timing is supplied, the 1st configuration line in the configuration file (not counting empty lines or comments) should be

```
timingsupplied=true
```

More on the configuration file is discussed below in the subsection "Using the Configuration File".

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

## Using the Configuration File

I have added this section before running the program because it is essential to understand how the configuration file works (and how you may need to change it) before trying to run the program.

The configuration file is designed to provide the user more freedom in how the program behaves on input data. It may be best to examine the default configuration file before writing one on your own and make sure it has the same name as the default configuration file. If you are using Windows, I would recommend using WordPad if you do not have another text editor such as Atom or Notepad++ to open the config file, as Notepad doesn't display the line breaks in the default config file.

Furthermore, to help yourself, you can add line comments in the configuration file by placing a hashtag "#" at the beginning of each comment line (as with Python). Comments can also be made after configuration lines by placing a "#". The program will ignore any text following the hashtag. Lastly, errors in the configuration file are also reported to the log file.

**Important:** If you wish to write your own configuration file and provide different settings for the various options that can be configured in this program, make sure you put the new options and settings in the same order as in the default configuration file. Otherwise, an error will occur.

The following sections discuss several changes you may have to make to your configuration file, based on the input files you will be providing the program.

### Tab Characters in the Input File

It is quite possible for the lines that contain the timing identifiers to contain tab characters ("\t"), especially if the user has decided to spread out the notes in the string lines. Due to the way that the program parses the input and assigns notes their length of time, the tab character causes problems. To solve this issue, the program will replace all tabs found in the timing lines with the number of spaces that correspond to a tab. By default, this is 8 spaces. However, in some text editors the number of spaces in a tab can be changed. Therefore, in the configuration file, a setting was added to specify how many spaces a tab should be replaced with. It is by default, set to 8:

```
tabspacing=8
```

Thus, before running the program, please check the number of spaces that are in a tab character for your text editor. For Windows users, Notepad follows the default and assigns each tab character to be equal to 8 spaces. Thus, you do not have to do anything in this case.

### Handling "Extra" Text

If the input file you have created includes extraneous text such as the song name at the top, a legend at the bottom, number of verses, etc., the program will still be able to parse the file for string lines and timing lines (assuming those were input correctly). However, there is a performance set-back and if you have found a tab file with no extra text or you wish to edit it so it has none, then change the configuration option "hasextra" in tabReader.config from "true" to "false", as so:

```
hasextra=false
```

This will provide a slight performance upgrade to the program, but can be ignored if you wish.

**Note:** This should only be done if there is no extra text in the input tab file, otherwise an error will occur.

### Creating a Legend

It is not uncommon for tabs to provide specifications within the string lines of how to play notes using a legend. I have provided an example to explain why this relates to the tab-reading program.

**Example:** Suppose I have a tab with the following legend.

```
h - hammer-on
p - pull-off
b - bend
```

For this program, you do not have to provide what each letter means, but it does need to know which characters will appear alongside the characters outlined in rule no. 1 in the section *Preparing an Input Tab File*. The way that you can specify this is through the configuration file. By default the "legend" option is blank. However, if I wanted to tell the program that I am passing in an input file with string lines that contain the characters in the above legend, I would change the "legend" line of the configuration file like so:

```
legend=hpb
```

*Observe:* I do not specify what h, p, and b mean, just that they will appear. Lastly, **note**, digits (0-9) and whitespace are not allowed to be in the legend.  

## Running the Program

Once you have installed the required files and have a tab file, say located at "C:\\Users\\Chami\\Desktop\\test_tab.txt", open your operating system's command line. Make sure you have retrieved your input file's **full** path unless the input file also resides in the same directory as the Python source files.

First, navigate to the directory where you have installed the Python source files. This is because the command below assumes "tabReader.py" is in the current working directory.

Now, run the following command:

```
py tabReader.py C:\\Users\\Chami\\Desktop\\test_tab.txt
```

After you run the program, an output HTML file encoded in *UTF-8* will be generated, in this case it will have the path "C:\\Users\\Chami\\Desktop\\test_tab_staff.html". To view this file, open it using a browser than can display the Unicode characters that are included such as [Mozilla Firefox 67.0 (64-bit)](https://www.mozilla.org/en-US/firefox/new/) or [Google Chrome Version 74.0.3729.169 (Official Build) (64-bit)](https://www.google.com/chrome/).

**Note:** If you run the same command again, the contents of this file will be overwritten, so if you wish to save the first output, I would rename the file or move it to another directory.

### The Log File

After the first time you run the program, a log file will be generated and placed in the same folder. All program output will be placed into this file unless the logging itself fails. This includes any errors that are reported, so this file should be checked in addition to the output file to make sure your program ran successfully. It is meant to be a more organized display of program output than simply printing to the console program you ran the program from.

**Note:** If a logging error occurs, that will be printed to the console.

It is important to realize however that the HTML file should also be checked carefully. The log file only reports if an error occurred in the program. If the user submitted incorrect input data, there are still circumstances where the program could execute correctly and still produce the wrong output. Consider the following.  

**Example:** Suppose the user creates a tab file where every string line is formatted incorrectly. The program will read through and ignore each line, thinking that they are not supposed to be string lines. The program will then return an empty staff with no errors thrown. This is still not the correct output however.

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
