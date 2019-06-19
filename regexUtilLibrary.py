"""
This file provides utility methods that allow easier use of the Python Regular Expressions module 're' by typeLibrary.py and configUtilLibrary.py

Compatibility Note: This file is what makes this project not incompatible with Python 2. Since Python 3 strings are represented in Unicode, the string.translate() method was changed. This method now requires a single argument, a translation table, which is different from the string.translate() method in Python 2.

author: Chami Lamelas
date: summer 2019
"""

REGEX_SPEC_CHRS = '.^$*+?{}()\\[]|:-' # The list of regex special characters was taken from the Python 3.7.3 documentation on the 're' module here: https://docs.python.org/3/library/re.html

"""
Given a Unicode string (that is a regular string as of Python 3), escapes all regex special characters in it and returns them as a raw string. That is, if "+" appears in the Unicode string in, it will become '\+' in the output raw string.
This means that characters will be interpreted as literals in a regex pattern as opposed to being interpreted differently. For example, in the case of "+" it would not be interpreted as 'more than one occurrence'.

params:
u - a Unicode string
"""
def escapeRegexSpecChrs(u):
    return r'{0}'.format(u.translate({ord(c): "\\"+c for c in REGEX_SPEC_CHRS}))
