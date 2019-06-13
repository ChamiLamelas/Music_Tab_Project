# Music Tab Project

The primary purpose of this project was to provide a program that takes an ASCII text file holding a bass guitar tab and converting it into sheet music. The sheet music is stored in an HTML file and can be displayed in a browser. Below, you will find an instructions manual on how to set-up and use this project.

**Date:** Summer 2019

## Getting Started

This section will inform you of the necessary prerequisites to run this program, the necessary files, and how to prepare program input files. It may be helpful for you to read about what data can be put into an ASCII text file. Here are some useful links:

* [Wikipedia Article on Text Files](https://en.wikipedia.org/wiki/Text_file)
* [Wikipedia Article on ASCII](https://en.wikipedia.org/wiki/ASCII)
* [An ASCII Table](http://www.asciitable.com/)
* For a discussion of text editors, and which one you may have on your computer refer to the subsection "Types of text editors" in the Wikipedia article on text files.

Furthermore, the sheet music output is an HTML file that is encoded in UTF-8. To read more about Unicode and character encodings, visit the [Wikipedia Article on Unicode](https://en.wikipedia.org/wiki/Unicode).

**Note:** the installation and running of this program has been tested *only* on Windows 10 using Python 3.7.2 and Python 3.7.3. Other versions of Python 3 have not been tested, but should be compatible. However, Python 2 is **NOT** compatible.

### Prerequisites

First, download a version of Python **3**. To do so, you can go to the [Python download page](https://www.python.org/downloads/). In the installation wizard, *make sure that Python is added to the system path* so that you can run the Python commands discussed in the section [Running the Program](#running-the-program).

Second, the program's output was tested in Mozilla Firefox 67.0 (64-bit) and Google Chrome Version 74.0.3729.169 (Official Build) (64-bit) on Windows Version 10.0.17763.503. So, it may be best to download one of those browsers. You can download the latest versions of these browsers below:

* [Firefox Download Page](https://www.mozilla.org/en-US/firefox/new/)
* [Chrome Download Page](https://www.google.com/chrome/)

### Installing

Each of the Python source files in the repository is necessary for the program to perform its intended purpose. To see what each one does, read the documentation at the top of each file. If you are interested, you can also read the documentation of each class and method in the source files.  

You can download the configuration file if you wish, if you run the program it will automatically generate one if it doesn't locate one on your computer.  

Make sure that *every* file you download is put in the *same* folder. Therefore, it may be suitable to download the entire repository as a ZIP file. To do this click the green button "Clone or download" and select "Download ZIP" from the dropdown menu.

## Preparing an Input Tab File

The input tab files follow the general format of tabs found on [Ultimate Guitar Tabs](https://www.ultimate-guitar.com/). The following subsections discuss some rules regarding how you should structure your input files. However, not every possible problem with an input tab file is addressed below. The error reporting system outlined in the exceptions library is meant to assist in helping you prepare a correct input tab file.

### Creating String Lines

String lines are lines of the input tab file that represent strings of the bass. This program offers the ability to read 2 types of string lines. Ones that are "simple" and ones that are not. I will provide a description of these 2 types followed by examples of both.

Lines that are "simple" string lines satisfy the following 4 properties:

**(1)** The first non-whitespace character must be G, D, A, or E followed by a "|" or just be "|"
**(2)** Following the first non-whitespace character, a sequence of only the following characters:

* vertical bar: "|"
* hyphen: "-"
* digits (0-9)
* any characters in the playing legend, see [Creating a Playing Legend](#creating-a-playing-legend)

*Note: whitespace is not allowed!*

**(3)** The last non-whitespace character must be a "|"
**(4)** Be at least 3 characters long, not counting the whitespace at either end.

Lines that are not "simple" contain string data as represented by properties **1-4** above but with extraneous non-whitespace text on either end of it. This is different from extra text lines in input tab files which are discussed in the later section [Handling Extra Text](#handing-extra-text) Now, for some examples:

**Example:** Here is a simple string line. Note that it starts with "G" followed by a "|" (the 1st case of property **1**).

```
G|---0---1---3|
```

**Example:** Here is a simple string line. Note that it starts with a "|" (the 2nd case of property **1**). This example could appear in a tab file where the strings are only identified earlier on in the file.

```
|0--1--2|
```

**Example:** Here is a simple string line. Note that it has some whitespace at the front. This is allowed.

```
                G|1--2|
```

**Example:** Here is a string line that is not simple. Note that there is extra text present at the front.

```
This is for the first verse     G|1---3--2|
```

**Example:** Here is a string line that is not simple. Note that there is extra text present at the front and back.

```
This is for the first verse     G|1---3--2|     Let the last note ring.
```

**Example:** Here is a line that is neither type of string line. While it may appear to be a non-simple string line because it has extra text, the string data that matches properties **1-4** cannot be broken up by either whitespace or non-whitespace!

```
This is for the first verse     G|1--3--2 Let this note ring 3--|
```

By default, string lines are assumed to be simple. If you have a file that has non-simple string lines please change this line in the configuration file from:

```
SIMPLE_STRING_LINES=true
```

to the following:

```
SIMPLE_STRING_LINES=false
```

More on the configuration file is discussed below in the section [Using the Configuration File](#using-the-configuration-file).

**Note:** There will be a performance decrease if the file has non-simple string lines because the program must locate the ends (the bar lines) of the segment of string data.

### Creating Timing Lines

There are 3 primary things to consider when creating timing lines.

**(1)** Lines that are meant to list the timings of notes that are played must be made up of *ONLY* the following characters and must contain at least **1** non-whitespace character.

* newline/carriage return: "\n" (at the end)
* tab: "\t"
* tie marking: "+"
* dot marking: "."
* space: " "
* *only* the uppercase letters that denote lengths of time: W, H, Q, E, and S

These lines should *only* be present if the timing is supplied in the tab, which is usually not the case. Make sure that if the timing is supplied, the 1st configuration line in the configuration file (not counting empty lines or comments) should be

```
TIMING_SUPPLIED=true
```

By default, this setting is false. More on the configuration file is discussed below in the section [Using the Configuration File](#using-the-configuration-file).

**(2)** The timing letter ID that signifies the length of a note is assumed to be located above the first digit of the fret that the note corresponds to. For example, if note on the E-string 10th fret (D) is meant to be a quarter note, the portion of the input tab that corresponds to this should appear as so:

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

**(3)** 2 notes should not overlap in such a way their fret numbers are not fully on top of each other. For example, the following would be a violation because 10 and 11 overlap. the note on the D-string would not be read properly

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

## Using the Configuration File

I have added this section before running the program because it is essential to understand how the configuration file works (and how you may need to change it) before trying to run the program.

The configuration file is designed to provide the user more freedom in how the program behaves on input data. It may be best to examine the default configuration file before writing one on your own and make sure it has the same name as the default configuration file. If you are using Windows, I would recommend using WordPad if you do not have another text editor such as Atom or Notepad++ to open the config file, as Notepad doesn't display the line breaks in the default config file.

Furthermore, to help yourself, you can add line comments in the configuration file by placing a hashtag "#" at the beginning of each comment line (as with Python). Comments can also be made at the end of configuration lines by placing a "#". The program will ignore any text following the hashtag. Lastly, errors in the configuration file are also reported to the log file.

**Important:** If you wish to write your own configuration file and provide different settings for the various options that can be configured in this program, make sure you put the new options and settings in the same order as in the default configuration file. Otherwise, an error will occur.

The following sections discuss several changes you may have to make to your configuration file, based on the input files you will be providing the program.

### Tab Characters in the Input File

It is quite possible for the lines that contain the timing identifiers to contain tab characters ("\t"), especially if the user has decided to spread out the notes in the string lines. Due to the way that the program parses the input and assigns notes their length of time, the tab character causes problems. To solve this issue, the program will replace all tabs found in the timing lines with the number of spaces that correspond to a tab. By default, this is 8 spaces. However, in some text editors the number of spaces in a tab can be changed. Therefore, in the configuration file, a setting was added to specify how many spaces a tab should be replaced with. It is by default, set to 8:

```
TAB_SPACING=8
```

Thus, before running the program, please check the number of spaces that are in a tab character for your text editor. For Windows users, Notepad follows the default and assigns each tab character to be equal to 8 spaces. Thus, you do not have to do anything in this case.

### Handling Extra Text

If the input file you have created includes extraneous text such as the song name at the top, a legend at the bottom, number of verses, etc., the program will still be able to parse the file for string lines and timing lines (assuming those were input correctly). However, there is a performance set-back and if you have found a tab file with no extra text or you wish to edit it so it has none, then change the configuration option "hasextra" in tabReader.config from "true" to "false", as so:

```
HAS_EXTRA=true
```

This will provide a slight performance upgrade to the program, but can be ignored if you wish.

**Notes:**

* This should only be done if there is no extra text in the input tab file, otherwise errors could occur in file reading.
* Lines that are made up entirely of whitespace do not count as "extra" text.
* To see the discussion of extra text at the end of string lines, go to [Creating String Lines](#creating-string-lines).
* There *cannot* be extra text in timing lines.

### Creating a Playing Legend

It is common for tabs to provide specifications within the string lines of how to play notes (to bend, hammer-on, pull-off, etc.) using a legend. In the tab-reading program, string lines need to have a specific definition in order to be identified by the program as explained in the section above [Preparing an Input Tab File](#preparing-an-input-tab-file). The legend configuration option as explained in the example below can be used to allow other characters to occur in string lines besides the ones listed explicitly in rule no. 1 in *Preparing an Input Tab File*.

**Example:** Suppose I have a tab with the following legend.

```
h - hammer-on
p - pull-off
b - bend
```

For this program, you do not have to provide what each letter means, but it does need to know which characters will appear in string lines as mentioned above. The way that you can specify this is through the configuration file. By default the "legend" option is blank. However, if I wanted to tell the program that I am passing in an input file with string lines that contain the characters in the above legend, I would change the "legend" line of the configuration file like so:

```
PLAYING_LEGEND=hpb
```

*Observe:* I do not specify what h, p, and b mean, just that they will appear. Lastly, **note**, digits (0-9) and whitespace are not allowed to be in the legend.  

### Creating a Timing Legend

In order for the program to properly parse the timing lines in the input tab file, it needs to know which symbols will occur in the timing lines to map them to tie symbols, dot symbols, and the different length notes. That is, there must be symbols for the following:

* Tie symbol (+ by default)
* Dot symbol (. by default)
* Whole note (W by default)
* Half note (H by default)
* Quarter note (Q by default)
* Eighth note (E by default)
* 16th note (S by default)
* 32nd note (T by default)
* 64th note (F by default)
* 128th note (O by default)  

These are provided to the program by the user as a **10 character** string *matching the above order* in the configuration file on the line marked "TIMING_SYMBOL". It is essential that the symbols are provided in that order. As an example, consider the default configuration file's setting on this line using the default values listed above:

```
TIMING_SYMBOLS=+.WHQESTFO
```

Here it can be seen that the tie symbol is 1st, then the dot symbol, followed by the timing notes in decreasing time order as listed above.

**Note:** The sheet music representations of these symbols are Unicode characters that cannot be changed and are taken from [this PDF](https://unicode.org/charts/PDF/U1D100.pdf).

## Running the Program

Once you have installed the required files and have a tab file, say located at "C:\\Users\\Chami\\Desktop\\test_tab.txt", open your operating system's command line. Make sure you have retrieved your input file's **full** path unless the input file also resides in the same directory as the Python source files.

First, navigate to the directory where you have installed the Python source files. This is because the command below assumes "tabReader.py" is in the current working directory.

Now, run the following command:

```
py tabReader.py C:\\Users\\Chami\\Desktop\\test_tab.txt
```

After you run the program, an output HTML file encoded in *UTF-8* will be generated, in this case it will have the path "C:\\Users\\Chami\\Desktop\\test_tab_staff.html". To view this file, open it using a browser than can display the Unicode characters that are included such as [Mozilla Firefox 67.0 (64-bit)](https://www.mozilla.org/en-US/firefox/new/) or [Google Chrome Version 74.0.3729.169 (Official Build) (64-bit)](https://www.google.com/chrome/).

**Note:** If you run the same command again, the contents of this file will be overwritten, so if you wish to save the first output, I would rename the file or move it to another directory.

### Understanding The Log File

After the first time you run the program, a log file will be generated and placed in the same folder. It is meant to be a more organized display of program output than simply printing to the console program you ran the program from. All program output will be placed into this file unless the logging itself fails. It is important to note that the log file will not only display error messages of problems that arose in program execution. This will be explained using the following example:

Suppose the program executes on a test file successfully and the log file reports the following. The program doesn't provide line numbers, but I have added them for convenience.

```
1) [2019-06-10 15:39:56.224618][> Log >] New Log Session started.
2) [2019-06-10 15:39:56.224618][Info] Successfully located input file "C:\Users\Chami\Desktop\test.txt" in program args. Beginning tab-reading program configuration...
3) [2019-06-10 15:39:56.224618][Info] Configuration file was found.
4) [2019-06-10 15:39:56.224618][Info] Configuration file was loaded and its contents were read successfully. Beginning tab-reading...
5) [2019-06-10 15:39:56.224618][Info] Input tab file "C:\Users\Chami\Desktop\test.txt" was opened and closed successfully.
6) [2019-06-10 15:39:56.225615][Info] Song building of the data from "C:\Users\Chami\Desktop\test.txt" finished without any parsing errors. 25 (ii) out of the 25 (i) loaded lines were parsed successfully.
7) [2019-06-10 15:39:56.225615][Info] 10 (iii) out of the 25 (ii) read lines were interpreted as string lines and timing lines. 6 (iv) Measure objects were created.
8) [2019-06-10 15:39:56.232632][Info] Output HTML file "C:\Users\Chami\Desktop\test_staff.html" was opened and Song data was written successfully before closing.
9) [2019-06-10 15:39:56.232632][Info] Tab-reading and sheet music generation was completed successfully in 0.008014 seconds.
```

Observe that lines 2-9 provide a timeline of the execution of the program. If error messages were to occur after some of these lines, it provides you with an easier way to diagnose the problem. That is, you will know which parts of the program executed successfully. However, lines 6 and 7 provide a little more than that. The program stores the input data by parsing the input tab file and then organizing into a set of new structures or objects (details on their implementation can be found in typeLibrary.py). If an explicit error is encountered in this process, then an error message would appear after line 5 above. If no error occurs, then you will see 2 lines similar to line 6 and 7 above. These lines tell you a few things. The last 2 are the most likely to be helpful as they address issues that are more likely to occur.

* How many lines were loaded from the input tab file. This is equal to 25 in this example, but is denoted as (ii) for clarity. This is useful for telling you whether the entire file was even read properly.
* How many lines were parsed from the set of loaded lines. This is equal to 25 in this example (as it should be if the program was successful) and is denoted as (i). This is useful for telling you whether the program missed some lines.
* How many lines were interpreted as string or timing lines. This is equal to 10 in this example and is denoted as (iii). This is useful for telling you whether all the lines you intended to be strings or timing lines were interpreted by the program as so.
* How many "things" in the input tab file were interpreted as measures. This is equal to 6 in this example and is denoted as (iv). The program stores anything between two horizontal bars "|" in a "Measure object", whether timing has been supplied or not. Therefore, this - similar to the 3rd bullet - gives you an idea of how much of the input tab file was read based on the bars you put in the input file.

**Note:** If a logging error occurs, that will be printed to the console.

It is important to realize however that the HTML file should also be checked carefully. The log file only reports *some* details of the program's execution and errors occurring in the program. If the user submitted incorrect input data, there are still circumstances where the program could execute correctly and still produce the wrong output. Consider the following.  

**Example:** Suppose the user creates a tab file where every string line is formatted incorrectly. The program will read through and ignore each line, thinking that they are not supposed to be string lines. The program will then return an empty staff with no errors thrown. This is still not the correct output however.

### Note about Cygwin

If you are interested in using Cygwin to run the program, I encountered an error with the time logging when I used Cygwin. After some research I found it could have been caused by Cygwin updating the Windows time zone environmental variable in such a way that Windows failed to interpret it correctly and switched to a default time zone (which seemed to be 1 hour after Greenwich Mean Time (GMT)). I wasn't confident about editing system environmental variables, which can be done through Cygwin, so I decided it was best to use Windows Command Prompt.

### Output and HTML

The reason that the staff output is displayed in an HTML file as opposed to an ASCII text file is to allow the display of the musical symbols which are Unicode characters whose codes can be found in this [PDF](https://unicode.org/charts/PDF/U1D100.pdf). Furthermore, the installation of either [Mozilla Firefox 67.0](https://www.mozilla.org/en-US/firefox/new/) or [Google Chrome](https://www.google.com/chrome/) was recommended because they were able to display these Unicode characters while Microsoft Edge could not.

## Future Development

If interested, here are possible upgrades that would be in later versions of the project.

* Using keys alongside the input file to output better sheet music that doesn't have to attach "#" to every sharped note.
* Support for non-standard tuning (G, D, A, E).
* A version for instruments other than a 4-string bass.

## Built With

* [Python 3.7.2](https://www.python.org/downloads/) - Python version. View the list of versions on the website.
* [Atom](https://atom.io/) - IDE I used for development.

## Authors

* **Chami Lamelas** - *Developer* - [LiquidsShadow](https://github.com/LiquidsShadow)

## Acknowledgments

* [PurpleBooth](https://github.com/PurpleBooth) - wrote the template for this file
