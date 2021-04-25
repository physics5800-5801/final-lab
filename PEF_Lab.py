#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""FIXME Provides NumberList and FrequencyDistribution, classes for statistics.

FIXME
NumberList holds a sequence of numbers, and defines several statistical
operations (mean, stdev, etc.) FrequencyDistribution holds a mapping from
items (not necessarily numbers) to counts, and defines operations such as
Shannon entropy and frequency normalization.
"""

######################################################################
## Imports 
######################################################################

import sys
import Experiment as exp

######################################################################
## Authorship Information
######################################################################

__author__ = "Conner Graham"
__copyright__ = "Copyright (c) 2021, The Ohio State University"
__credits__ = ["Shyon Deshpande"]

__license__ = "GPL 3.0-or-later"
__version__ = "1.0.1"
__maintainer__ = "Conner Graham"
__email__ = "connergraham888@gmail.com"
__status__ = "Development"

######################################################################
# Helper Methods
######################################################################

def print_welcome_banner():
    """
    Prints the program welcome banner and instructions.
    """

    print("Welcome! Create your own list of rectangles.")
    print("You will be asked to provide information about each rectangle in your list by name.")
    print("Type the word 'stop' for the rectangle name when you are done.\n")

def print_menu_options():
    """
    TODO.
    """

    print("MENU")

def get_option(min=0, max=sys.maxsize):
    """TODO.

    Parameters
    ----------
    min : int
        TODO.
    max : int
        TODO.

    Returns
    -------
    option : int
        TODO.
    """
    
    option = -1
    while (option < min or option > max):
        try:
            option = int(input('Select an option: '))
            if (option < min or option > max):
                print('ERROR: invalid option: valid options are', min, '-', max)
        except:
            print('ERROR: invalid input: option must be a valid integer')   
    return option

######################################################################
# Main Method
######################################################################

def main():
    print_welcome_banner()

    option = 1
    PE_exp = exp.Experiment('PE_exp')
    while (option > 0):
        print_menu_options()
        print(PE_exp.get_name())
        option = get_option()
        print()
        

if __name__ == "__main__":
    main()
