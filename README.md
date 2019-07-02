# Music Tab Project

The primary purpose of this project was to provide a program that takes an ASCII text file holding a bass guitar tab and converting it into sheet music. The sheet music is stored in an HTML file and can be displayed in a browser. Below, you will find an instructions manual on how to set-up and use this project.

**Date:** Summer 2019

## Table of Contents

Here is an ordered outline of this file's contents:

* [Getting Started](#getting-started)
	* [Prerequisites](#prerequisites)
	* [Installing the Program](#installing-the-program)
* [Preparing an Input Tab File](#preparing-an-input-tab-file)
	* [Creating String Lines](#creating-string-lines)
	* [Creating Timing Lines](#creating-timing-lines)
* [Using the Configuration File](#using-the-configuration-file)
	* [Tab Characters in the Input File](#tab-characters-in-the-input-file)
	* [Handling Extra Text](#handling-extra-text)
		* [Warning about Multiple Instances of Extra Text Between String and Timing Lines](#warning-about-multiple-instances-of-extra-text-between-string-and-timing-lines)
		* [Warning about Extra Text at the Ends of String Lines](#warning-about-extra-text-at-the-ends-of-string-lines)
	* [Keeping Extra Text](#keeping-extra-text)
	* [Creating a Playing Legend](#creating-a-playing-legend)
	* [Creating a Timing Legend](#creating-a-timing-legend)
* [Running the Program](#running-the-program)
	* [Understand the Log File](#understanding-the-log-file)
	* [Note about Cygwin](#note-about-cygwin)
	* [Output and HTML](#output-and-html)
* [Future Development](#future-development)
* [Built With](#built-with)
* [Authors](#authors)
* [Acknowledgments](#acknowledgments)

## Getting Started

This section will inform you of the necessary prerequisites to run this program and the necessary files to install. It may be helpful for you to read about what data can be put into an ASCII text file. Here are some useful links:

* [Wikipedia Article on Text Files](https://en.wikipedia.org/wiki/Text_file)
* [Wikipedia Article on ASCII](https://en.wikipedia.org/wiki/ASCII)
* [An ASCII Table](http://www.asciitable.com/)
* For a discussion of text editors, and which one you may have on your computer refer to the subsection "Types of text editors" in the Wikipedia article on text files.

Furthermore, the sheet music output is an HTML file that is encoded in the UTF-8 character encodings. To read more about Unicode and character encodings, visit the [Wikipedia Article on Unicode](https://en.wikipedia.org/wiki/Unicode).

You *should* be able to use Python version **3.4** or later. However, the installation and running of this program has been tested **only** using Python 3.7.2 and Python 3.7.3. If your Python version is too old, the program will not try to run and an error will appear in the command line you use to run the program (see the later section [Running the Program](#running-the-program)).

**Note:** This program has only been tested on Windows 10.

### Prerequisites

First, it is recommended to download one of the versions of Python mentioned above. To do so, you can go to the [Python download page](https://www.python.org/downloads/). In the installation wizard, *make sure that Python is added to the system path* so that you can run the Python commands discussed in the section [Running the Program](#running-the-program). To check that you have installed the correct version of Python *and* that has been added to your path, open your operating system's command line. To learn about what a command line is, here is a [Wikipedia Article](https://en.wikipedia.org/wiki/Command-line_interface) and a [Code Academy Tutorial](https://www.codecademy.com/learn/learn-the-command-line/modules/learn-the-command-line-navigation-u). Once you have opened your command line and assuming that you downloaded one of the versions mentioned above, type the following:

```
py --version
```

Here is the output I get running Python 3.7.2:

```
Python 3.7.2
```

Second, the program's output was tested in Mozilla Firefox 67.0 (64-bit) and Google Chrome Version 74.0.3729.169 (Official Build) (64-bit) on Windows Version 10.0.17763.503. So, it may be best to download one of those browsers. You can download the latest versions of these browsers below:

* [Firefox Download Page](https://www.mozilla.org/en-US/firefox/new/)
* [Chrome Download Page](https://www.google.com/chrome/)

Furthermore, since examples of program output are provided later in this file, it may be best for you to download one of these browsers before continuing.

### Installing the Program

*All* of the Python source files (files with the ".py" extension) in the repository are necessary for the program to perform its intended purpose. To see what each one does, read the documentation at the top of each file. If you are interested, you can also read the documentation of each class and method in the source files.

Make sure that *every* file you download is put in the *same* folder. Therefore, it may be suitable to download the entire repository as a ZIP file. To do this click the green button "Clone or download" and select "Download ZIP" from the dropdown menu.

You can download the configuration file if you wish, if you run the program it will automatically generate one if it doesn't locate one on your computer.  
If you are not planning on creating your own GitHub repository for this project, you can delete the ".gitignore" file from your computer.

## Preparing an Input Tab File

The input tab files follow the general format of tabs found on [Ultimate Guitar Tabs](https://www.ultimate-guitar.com/). The following subsections discuss some rules regarding how you should structure your input files. However, not every possible problem with an input tab file is addressed below. The error reporting system outlined in the exceptions library is meant to assist in helping you prepare a correct input tab file.

### Creating String Lines

String lines are lines of the input tab file that represent strings of the bass. This program offers the ability to read 2 types of string lines. String lines that contain non-whitespace or "extra" text at the beginning and/or at the end and string lines that do not. I will refer to the latter as "simple" string lines.

Lines that are "simple" string lines satisfy the following 4 properties:

**(1)** The first non-whitespace character must either be a "|" or be from the set {G, g, D, d, A, a, E, e} followed by a "|".

If you decide to provide string names from the set above, they will be checked by the program. That is, the program expects the strings to be ordered top to bottom from the G-string to the E-string like in the following example.

> **Example:** Here is an example of top to bottom G->D->A->E ordering.

```
G|1---|
D|-2--|
A|--3-|
E|---4|
```

Here is one possible example of string lines that have been ordered incorrectly.

> **Example:** The program would flag these input string lines as invalid, because they do not follow G->D->A->E vertical order.

```
E|1---|
A|-2--|
D|--3-|
G|---4|
```

**However**, if you do not provide the string names for each string, *no* check is done and it is assumed you have entered the strings with the G->D->A->E top to bottom ordering.

**(2)** Following the first non-whitespace character, a sequence of only the following characters:

* vertical bar: "|"
* hyphen: "-"
* digits (0-9)
* any characters in the playing legend, see [Creating a Playing Legend](#creating-a-playing-legend)

***Note: whitespace is not allowed!***

**(3)** The last non-whitespace character must be a "|"  
**(4)** Be at least 3 characters long, not counting the whitespace at either end.

Lines that are not "simple" contain string data as represented by properties **1-4** above but with non-whitespace text at the beginning* and/or the end.

**Note (\*):** The extraneous non-whitespace text at the beginning *cannot* contain a vertical bar character "|". Otherwise, the program will think that this is the beginning of a segment of string data. Vertical bars can be included in the extra
text following the segment of string data and in lines that are meant to be entirely extra text (see later section [Handling Extra Text](#handling-extra-text)).

> **Example:** Here is a simple string line. Note that it starts with "G" followed by a "|" (the 1st case of property **1**).

```
G|---0---1---3|
```

> **Example:** Here is a simple string line. Note that it starts with a "|" (the 2nd case of property **1**). This example could appear in a tab file where the strings are only identified earlier on in the file.

```
|0--1--2|
```

> **Example:** Here is a simple string line. Note that it has some whitespace at the front. This is allowed.

```
                G|1--2|
```

> **Example:** Here is a string line that is not simple. Note that there is extra text present at the front.

```
This is for the first verse     G|1---3--2|
```

> **Example:** Here is a string line that is not simple. Note that there is extra text present at the front and back.

```
This is for the first verse     G|1---3--2|     Let the last note ring.
```

> **Example:** Here is a line that is neither type of string line. While it may appear to be a non-simple string line because it has extra text, the string data that matches properties **1-4** cannot be broken up by either whitespace or non-whitespace!

```
This is for the first verse     G|1--3--2 Let this note ring 3--|
```

By default, string lines are assumed to not be simple. Therefore, if you wish to create an input file with no extra text (discussed more in [Handling Extra Text](#handling-extra-text)), that includes making all string lines "simple".

**Note:** There will be a performance decrease if the file has non-simple string lines because the program must locate the ends (the bar lines) of the segment of string data.

### Creating Timing Lines

There are 3 primary things to consider when creating timing lines.

**(1)** Lines that are meant to list the timings of notes that are played must be made up of *ONLY* the following characters and must contain at least **1** non-whitespace character.

* newline/carriage return: "\n" (at the end)
* tab: "\t"
* space: " "
* *only* the characters that have been specified as the timing symbol, dot symbol, and timing symbols in the timing legend. Please read the section [Creating a Timing Legend](#creating-a-timing-legend) for more.

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

I have added this section before running the program because it is essential to understand how the configuration file - which is called "tabReaderCONFIG.config" - works (and how you may need to change it) before trying to run the program.

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

If the input file you have created includes extraneous text either as their own lines (such as a song name at the top) or at the beginning or end of string lines, the program will still be able to parse the file for string lines and timing lines (assuming those were input correctly). However, there is a performance set-back as the program must identify the string data. By default, the configuration file has the has extra option as true since most tab files have extraneous text. However, if you have found a tab file with no extra text or you removed all the extraneous text from one, change the following setting in the configuration file from

```
HAS_EXTRA=true
```

to the following:

```
HAS_EXTRA=false
```

**Notes:**

* You cannot have extra text in the middle of string lines. This was discussed previously in the section [Creating String Lines](#creating-string-lines).
* If you set HAS_EXTRA to "false" and there is extra text in the input file, then errors could occur in the file reading.
* If you set HAS_EXTRA to "false" and TIMING_SUPPLIED to "false" when there is timing information in an input file, an error will most likely occur as this is a special case of the previous note. That is, the timing lines are treated as "extra text" by the program.  
* Lines that are made up entirely of whitespace do not count as "extra" text.
* There *cannot* be extra text in timing lines. That is, text that does not appear in the timing legend (see section [Creating a Timing Legend](#creating-a-timing-legend)).
* However, extra text may appear in between timing and string lines.

> **Example:** Here, extra text is placed in between the last 2 string lines (representing the A and E strings).

```
  Q  Q  Q  S S E   Q  Q  Q  S S E   Q  Q  Q  S S E

|----5--4--2-0---|----5--4--2-0---|----5-----------|

|----------------|----------------|----------7-5---|

|-3--------------|-3--------------|-3-----7--------|
                                              Let this last note ring!
|--------------3-|--------------3-|--------------3-|
```

> Here is the output. It will be used in the observation following the next example.

```
                                                Let this last note ring!
        -𝅘𝅥-                               -𝅘𝅥-                               -𝅘𝅥-                         
               𝅘𝅥                                 𝅘𝅥                                                      
||-------------------𝅘𝅥𝅯-------------|-------------------𝅘𝅥𝅯-------------|-------------------𝅘𝅥𝅯-------------|
||                         𝅘𝅥𝅯       |                         𝅘𝅥𝅯       |                         𝅘𝅥𝅯       |
||---------------------------------|---------------------------------|---------------------------------|
||                                 |                                 |             𝅘𝅥                   |
||---------------------------------|---------------------------------|---------------------------------|
|| 𝅘𝅥                               | 𝅘𝅥                               | 𝅘𝅥                               |
||---------------------------------|---------------------------------|---------------------------------|
||                                 |                                 |                                 |
||-------------------------------𝅘𝅥𝅮-|-------------------------------𝅘𝅥𝅮-|-------------------------------𝅘𝅥𝅮-|
```

> **Example:** Here, extra text is placed in between the timing line and the first string line (representing the G-string).

```
   H      Q    E  E    H      H        Q  Q  Q  S E S   Q  Q  Q  E  S
                                                          Play these last 4 notes muted!
|-------------------|---------------||----5--4--2-0---|----5--4--2--0--||

|-------------------|---------------||----------------|----------------||

|--1------1----1----|---------------||-3--------------|-3--------------||

|-----------------3-|--3------3-----||--------------3-|----------------||
```

> Here is the output that will be used in the following observation.

```
                                                        Play these last 4 notes muted!
                                 -𝅘𝅥-                               -𝅘𝅥-                    
                                        𝅘𝅥                                 𝅘𝅥               
|------------------|------|-------------------𝅘𝅥𝅯-------------|-------------------𝅘𝅥𝅮·-------|
|                  |      |                         𝅘𝅥𝅮       |                          𝅘𝅥𝅯 |
|------------------|------|---------------------------------|----------------------------|
|                  |      |                                 |                            |
|------------------|------|---------------------------------|----------------------------|
|                  |      | 𝅘𝅥                               | 𝅘𝅥                          |
|------------------|------|---------------------------------|----------------------------|
|_𝅗𝅥♯__𝅘𝅥♯__𝅘𝅥𝅮♯       |      |                                 |                            |
|----------------𝅘𝅥𝅮_|_𝅗𝅥__𝅗𝅥-|-------------------------------𝅘𝅥𝅯-|----------------------------|
```

*Observe:* the 2 examples of extra text, "Let this last note ring!" and "Play these last 4 notes muted!", were moved from their original places in the input tab file when they appear in the output sheet music. This is for the following reasons.
* The program interprets any extra text between string and timing lines as occurring "before" the measures that are represented in the segment of the input file taken up by the 4 string lines and the timing line.
* Furthermore, the program places those sets of measures together as well in the sheet music to preserve the user's input formatting. Since extra text does not appear in sheet music, the program chooses to place the extra text before these measures. Hence, the text appears above the staff and is slightly offset because the sheet music has different spacing than the tab.

#### Warning about Multiple Instances of Extra Text Between String and Timing Lines

Putting extra text in between string and notes lines multiple times for the same group of measures will result in the extra text being placed in a line horizontally above the measures. Again, this is due to the fact that extra text cannot be placed within the output sheet music and is moved above it. This will be illustrated in the following example.

> **Example:** Consider the following segment from a possible input tab file. It contains a few measures of string data with extra text between the timing and string lines.

```
  Q  Q  Q  S S E   Q  Q  Q  S S E   Q  Q  Q  S S E
			      separating test #1
|----5--4--2-0---|----5--4--2-0---|----5-----------|
			      separating test #2
|----------------|----------------|----------7-5---|
			      separating test #3
|-3--------------|-3--------------|-3-----7--------|
			      separating test #4
|--------------3-|--------------3-|--------------3-|      
```

> Here is the output that will be used in the following observation.

```
			       separating test #1                                separating test #2                                separating test #3                                separating test #4
      -𝅘𝅥-                               -𝅘𝅥-                               -𝅘𝅥-                          
	     𝅘𝅥                                 𝅘𝅥                                                       
|-------------------𝅘𝅥𝅯-------------|-------------------𝅘𝅥𝅯-------------|-------------------𝅘𝅥𝅯-------------||
|                         𝅘𝅥𝅯       |                         𝅘𝅥𝅯       |                         𝅘𝅥𝅯       ||
|---------------------------------|---------------------------------|---------------------------------||
|                                 |                                 |             𝅘𝅥                   ||
|---------------------------------|---------------------------------|---------------------------------||
| 𝅘𝅥                               | 𝅘𝅥                               | 𝅘𝅥                               ||
|---------------------------------|---------------------------------|---------------------------------||
|                                 |                                 |                                 ||
|-------------------------------𝅘𝅥𝅮-|-------------------------------𝅘𝅥𝅮-|-------------------------------𝅘𝅥𝅮-||
```

*Observe:* Since the program cannot keep the extra text separating the timing and string lines on the staff, the extra text is placed above the staff. The whitespace used as formatting in the input tab file is kept.

#### Warning about Extra Text at the Ends of String Lines

While the program saves the extra text surrounding string data in a string line, it places it in the sheet music in a somewhat confusing manner. I will provide an example to illustrate the program behavior, and then explain it below.

> **Example:** Consieder the following segment from a possible input tab file. It contains a few measures of string data with extra text on both ends.

```
				Q  Q  Q  S S E   Q  Q  Q  S S E   Q  Q  Q  S S E

starting extra text #1        |----5--4--2-0---|----5--4--2-0---|----5-----------|      ending extra text #1

starting extra text #2        |----------------|----------------|----------7-5---|      ending extra text #2

starting extra text #3        |-3--------------|-3--------------|-3-----7--------|      ending extra text #3

starting extra text #4        |--------------3-|--------------3-|--------------3-|      ending extra text #4
```

> Here is the output that will be used in the following observation.

```
starting extra text #1; starting extra text #2; starting extra text #3; starting extra text #4
        -𝅘𝅥-                               -𝅘𝅥-                               -𝅘𝅥-                         
               𝅘𝅥                                 𝅘𝅥                                                      
||-------------------𝅘𝅥𝅯-------------|-------------------𝅘𝅥𝅯-------------|-------------------𝅘𝅥𝅯-------------|
||                         𝅘𝅥𝅯       |                         𝅘𝅥𝅯       |                         𝅘𝅥𝅯       |
||---------------------------------|---------------------------------|---------------------------------|
||                                 |                                 |             𝅘𝅥                   |
||---------------------------------|---------------------------------|---------------------------------|
|| 𝅘𝅥                               | 𝅘𝅥                               | 𝅘𝅥                               |
||---------------------------------|---------------------------------|---------------------------------|
||                                 |                                 |                                 |
||-------------------------------𝅘𝅥𝅮-|-------------------------------𝅘𝅥𝅮-|-------------------------------𝅘𝅥𝅮-|
ending extra text #1; ending extra text #2; ending extra text #3; ending extra text #4
```

*Observe:* the extra text preceding the string lines in the example input (marked \"starting extra text #1-4\") is placed in a line separated by semi-colons directly above the output sheet music (observe all whitespace surrounding the extra text is stripped). Similarly, the extra text succeeding the string lines in the example input (marked \"ending extra text #1-4\") is placed in a line separated by semi-colons directly below the output sheet music. This is because the extra text would no longer align with the notes/string it aligns with in the input tab file since the notes have been converted into sheet music. The same logic applies to the ending text.

> **Conclusion:** It may be best to avoid putting multiple instances of extra text between string and timing lines as well as placing text on the ends of the string lines to avoid confusion when the extra text is displayed in the output sheet music.


### Keeping Extra Text

There is also a configuration option to specify whether or not you wish to keep the extra text in the input tab file. That is, the extra text that appears in the input tab will appear in the same places in the output HTML file. By default, this configuration option is set to true. However, if you wish to not keep the extra text, change:

```
KEEP_EXTRA=true
```

to the following:

```
KEEP_EXTRA=false
```                

**Notes:**

* You cannot have ```KEEP_EXTRA=true``` if ```HAS_EXTRA=false```.
* If you have set ```KEEP_EXTRA=false```, the output HTML will use the empty lines in the input tab file that are *not* between timing and string lines to place the rows of Measures. I will show this in an example.

> **Example:** Suppose I have the following input tab file (with extra text) and I have set 'KEEP_EXTRA' to false. I have marked the empty lines for clarity.

```
PRESENCE OF THE LORD (Bassline)
*EMPTY LINE*
*EMPTY LINE*
Gtr I (E A D G) - 'Ric Grech - Bass'
*EMPTY LINE*
 Intro
*EMPTY LINE*
  Q=60
*EMPTY LINE*
 4/4
*EMPTY LINE*
  Gtr I
*EMPTY LINE*
  Q  Q  Q  S S E   Q  Q  Q  S S E   Q  Q  Q  S S E
*EMPTY LINE*
|----5--4--2-0---|----5--4--2-0---|----5-----------|
*EMPTY LINE*
|----------------|----------------|----------7-5---|
*EMPTY LINE*
|-3--------------|-3--------------|-3-----7--------|
*EMPTY LINE*
|--------------3-|--------------3-|--------------3-|
*EMPTY LINE*
*EMPTY LINE*
*EMPTY LINE*
*EMPTY LINE*
*EMPTY LINE*
                   1st Verse
*EMPTY LINE*
  Q  Q  Q  S S E    Q..   S Q  S S S S   Q  +S  S E +S  S E +S  S E
*EMPTY LINE*
|----5--4--2-0---||--------------------|----------------------------|
*EMPTY LINE*
|----------------||--------------------|----------7-(7)-------------|
*EMPTY LINE*
|-3--------------||-3------------5---5-|--------7---------7-(7)-----|
*EMPTY LINE*
|--------------3-||-------3-3------7---|-5--(5)---------5-------5-3-|
```

*Observe:* There are **7** empty lines that occur before the first 3 measures that are not between timing and string lines. Next, there are 4 empty lines between the timing and string lines. Then, there are **6** empty lines between the first 3 measures and the second 3 measures. Lastly, there are 4 more empty lines between timing and string lines.

> Now, here is the output HTML file. Again, I have marked the empty lines for clarity.

```
*EMPTY LINE*
*EMPTY LINE*
*EMPTY LINE*
*EMPTY LINE*
*EMPTY LINE*
*EMPTY LINE*
*EMPTY LINE*
        -𝅘𝅥-                               -𝅘𝅥-                               -𝅘𝅥-                         
               𝅘𝅥                                 𝅘𝅥                                                      
||-------------------𝅘𝅥𝅯-------------|-------------------𝅘𝅥𝅯-------------|-------------------𝅘𝅥𝅯-------------|
||                         𝅘𝅥𝅯       |                         𝅘𝅥𝅯       |                         𝅘𝅥𝅯       |
||---------------------------------|---------------------------------|---------------------------------|
||                                 |                                 |             𝅘𝅥                   |
||---------------------------------|---------------------------------|---------------------------------|
|| 𝅘𝅥                               | 𝅘𝅥                               | 𝅘𝅥                               |
||---------------------------------|---------------------------------|---------------------------------|
||                                 |                                 |                                 |
||-------------------------------𝅘𝅥𝅮-|-------------------------------𝅘𝅥𝅮-|-------------------------------𝅘𝅥𝅮-|
*EMPTY LINE*
*EMPTY LINE*
*EMPTY LINE*
*EMPTY LINE*
*EMPTY LINE*
*EMPTY LINE*
       -𝅘𝅥-                                                                                                                    
              𝅘𝅥                                                                                                               
|-------------------𝅘𝅥𝅯-------------|-----------------------------------------|----------------𝅘𝅥𝅮__𝅘𝅥𝅯----------------------------|
|                         𝅘𝅥𝅯       |                                         |                                                |
|---------------------------------|-----------------------------------------|------------------------------------------------|
|                                 |                                         |          𝅘𝅥𝅯                    𝅘𝅥𝅮__𝅘𝅥𝅯             |
|---------------------------------|---------------------𝄿-----𝅘𝅥𝅯-----------𝅘𝅥𝅯-|------------------------------------------------|
| 𝅘𝅥                               | 𝅘𝅥··                                     |                                                |
|---------------------------------|---------------------------------𝅘𝅥𝅯-------|------------------------------------------------|
|                                 |                                         | 𝅘𝅥__𝅘𝅥𝅯                    𝅘𝅥𝅯              𝅘𝅥𝅯       |
|-------------------------------𝅘𝅥𝅮-|---------𝅘𝅥𝅯-----𝅘𝅥-------------------------|----------------------------------------------𝅘𝅥𝅮-|
```

*Observe:* There are **7** empty lines before the first 3 measures of sheet music and then there are **6** more empty lines before the second 3 measures. The 2 sets of 4 empty lines between the timing and string lines in the input file are ignored, as well as the extra text "1st Verse" in the input tab file.

### Creating a Playing Legend

It is common for tabs to provide specifications within the string lines of how to play notes (to bend, hammer-on, pull-off, etc.) using a legend. The legend configuration option as explained in the example below can be used to allow other characters to occur in string lines besides the ones listed explicitly in rule **(1)** in [Preparing an Input Tab File](#preparing-an-input-tab-file).

> **Example:** Suppose I have a tab with the following legend.

```
h - hammer-on
p - pull-off
b - bend
```

For this program, you do not have to provide what each letter means, but it does need to know which characters will appear in string lines as mentioned above. The way that you can specify this is through the configuration file. By default the "playing legend" option is blank. However, if I wanted to tell the program that I am passing in an input file with string lines that contain the characters in the above legend, I would change the "playing legend" line of the configuration file like so:

```
PLAYING_LEGEND=hpb
```

*Observe:* I do not specify what h, p, and b mean, just that they will appear.

**Note:** The playing legend can only be made up of either lowercase or uppercase alphabet characters.

### Creating a Timing Legend

In order for the program to properly parse the timing lines in the input tab file, it needs to know which symbols will occur in the timing lines to map them to the following:

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

These are provided to the program by the user as a **10 character** string *matching the above order* in the configuration file on the line marked "TIMING_SYMBOLS". It is essential that the symbols are provided in that order. As an example, consider the default configuration file's setting on this line using the default values listed above:

```
TIMING_SYMBOLS=+.WHQESTFO
```

Here it can be seen that the tie symbol is 1st, then the dot symbol, followed by the timing notes in decreasing time order as listed above.

**Note:** The sheet music representations of these symbols are Unicode characters that cannot be changed and are taken from [this PDF](https://unicode.org/charts/PDF/U1D100.pdf).

## Running the Program

Once you have installed the required files and have a tab file, run the program using the following instructions:

* Open your operating system's command line; the same as in [Getting Started](#getting-started).
* Navigate to the directory to where you have downloaded the source files. This is because the commands below assume "tabReader.py" is in the current working directory. This can be done using the "change directory" command as explained in the [Wikipedia Article on this Command](https://en.wikipedia.org/wiki/Cd_(command)).
* Make sure that all your configuration settings have been updated as discussed above in the sections [Using the Configuration File](#using-the-configuration-file) and [Preparing an Input Tab File](#preparing-an-input-tab-file).
* If your input file is in the *same* directory as the source files, run the following command:

```
py tabReader.py <input file name including extension>
```

* If your input file is in a different directory, retrieve your input file's **full** path. Consider the following example for Windows:

> **Example:** Say my input tab file is located at "C:\\Users\\Chami\\Desktop\\test.txt". Then, I would run this command:

```
py tabReader.py C:\Users\Chami\Desktop\test.txt
```

**Note:** file path formatting differs per operating system, as shown in the [Wikipedia Article on Paths](https://en.wikipedia.org/wiki/Path_(computing)#Representations_of_paths_by_operating_system_and_shell).

After you run the program, an output HTML file encoded in the *UTF-8* character encoding will be generated, in this case it will have the path "C:\\Users\\Chami\\Desktop\\test_staff.html". To view this file, open it using a browser that can display Unicode characters in this encoding. For example: [Mozilla Firefox 67.0 (64-bit)](https://www.mozilla.org/en-US/firefox/new/) or [Google Chrome Version 74.0.3729.169 (Official Build) (64-bit)](https://www.google.com/chrome/).

**Note:** If you run the same command again, the contents of the HTML file will be overwritten. So, if you wish to save the first output, I would rename the file or move it to another directory.

### Understanding The Log File

After the first time you run the program, a log file called "tabReaderLOG.log" will be generated and placed in the same folder. It is meant to be a more organized display of program output than simply printing to the console program you ran the program from. All program output will be placed into this file unless the logging itself fails. It is important to note that the log file will display more information than just error messages of problems that arose in program execution. This will be explained using the following example:

Suppose the program executes on a test file successfully and the log file reports the following:

**Note:** The program does not provide line numbers in the log file (1-9) nor does it include the roman numerals (i-iv). I have added these 2 sets of markers to make the explanation of the log output example below easier to follow. Also, I have omitted the first 2 log session information lines and the times of each logged message from the example for clarity. However, these will be
shown in your own version of the log file.

```
1) [Info] Successfully located input file "test_files\test2.txt" in program arguments. Beginning tab-reading program configuration...
2) [Info] Configuration file was found and loaded successfully.
3) [Info] The contents of the configuration file were read successfully. Beginning tab-reading...
4) [Info] Input tab file "test_files\test2.txt" was opened and closed successfully.
5) [Info] Song building of the data from "C:\Users\Chami\Desktop\test.txt" finished without any parsing errors. 25 (ii) out of the 25 (i) loaded lines were read successfully.
6) [Info] 10 (iii) out of the 25 (ii) read lines were interpreted as string lines. 6 (iv) Measure objects were created.
7) [Info] Output HTML file "C:\Users\Chami\Desktop\test_staff.html" was opened and Song data was written successfully before closing.
8) [Info] Tab-reading and sheet music generation was completed successfully in 0.203173 seconds.
```

Observe that these lines provide a timeline of the execution of the program. If error messages were to occur after some of these lines, it provides you with an easier way to diagnose the problem. That is, you will know which parts of the program executed successfully. However, lines 5 and 6 provide a little more than that. The program stores the input data by parsing the input tab file and then organizing it into a set of new structures or objects (details on the objects' implementation can be found in typeLibrary.py). If an explicit error is encountered in this process, then an error message would appear after line 4 above. If no error occurs, then you will see 2 lines similar to line 5 and 6 above. These lines tell you a few things:

* How many lines were loaded from the input tab file. This is denoted as (i). In this example, it is equal to 25. This is useful for telling you whether the entire file was read properly.
* How many lines were parsed from the set of loaded lines. This is denoted as (ii). In this example, it is equal to 25 (as it should be if the program was successful) and is denoted as (ii). This is useful for telling you whether the program missed some lines.
* How many lines were interpreted or parse as string or timing lines. This is denoted as (iii). In this example, it is equal to 10. This is useful for telling you whether all the lines you intended to be strings or timing lines were interpreted by the program as so.
* How much data in the input tab file was interpreted as measures. This is denoted as (iv). In this example, it is equal to 6. The program stores anything between two horizontal bars "|" in a "Measure object", whether timing has been supplied or not. Therefore, this gives you an idea of how much of the input tab file was read based on the placement of the bars in the input file.

It is important to realize however that the HTML file should also be checked carefully. The log file only reports *some* details of the program's execution and errors occurring in the program. If the user submitted incorrect input data, there are still circumstances where the program could execute correctly and still produce the wrong output. Consider the following.  

> **Example:** Suppose the user creates a tab file where every string line is formatted incorrectly. The program will read through and ignore each line, thinking that they are not supposed to be string lines. The program will then return an empty staff with no errors thrown. This is still not the correct output however.

**Note:** If an error occurs in the logging process, its information will be printed to the console.

### Note about Cygwin

If you are interested in using Cygwin to run the program, I encountered an error with the time logging when I used Cygwin. After some research I found it could have been caused by Cygwin updating the Windows time zone environmental variable in such a way that Windows failed to interpret it correctly and switched to a default time zone (which seemed to be 1 hour after Greenwich Mean Time (GMT)). I wasn't confident about editing system environmental variables, which can be done through Cygwin, so I decided it was best to use Windows Command Prompt.

### Output and HTML

The reason that the staff output is displayed in an HTML file as opposed to an ASCII text file is to allow the display of the musical symbols which are Unicode characters whose codes can be found in this [PDF](https://unicode.org/charts/PDF/U1D100.pdf). Furthermore, the installation of either [Mozilla Firefox 67.0](https://www.mozilla.org/en-US/firefox/new/) or [Google Chrome](https://www.google.com/chrome/) was recommended because they were able to display these Unicode characters while Microsoft Edge could not.

## Future Development

If interested, here are possible upgrades that would be in later versions of the project.

* Compatibility with versions of Python older than 3.4. That is, find a replacement for the various Enums used throughout the project.
* Using keys alongside the input file to output better sheet music that doesn't have to attach "#" to every sharped note.
* Support for non-standard tuning (G, D, A, E).
* A version for instruments other than a 4-string bass.
* Saving the spacing between notes from the user's input tablature in the output sheet music representation. This would also better improve the placement of extra text in the output sheet music.
* Improving the output sheet music's spacing. That is, each line in the staff is actually the same length. Could possibly done using HTML tables.

## Built With

* [Python 3.7.2](https://www.python.org/downloads/) - Python version. View the list of versions on the website.
* [Atom](https://atom.io/) - IDE I used for development.

## Authors

* **Chami Lamelas** - *Developer* - [LiquidsShadow](https://github.com/LiquidsShadow)

## Acknowledgments

* [PurpleBooth](https://github.com/PurpleBooth) - wrote the template for this file
