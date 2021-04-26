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
from termcolor import cprint
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

    # FIXME
    print('Welcome! Create your own list of rectangles.')
    print('You will be asked to provide information about each rectangle in your list by name.')
    print('Type the word stop for the rectangle name when you are done.\n')
    return

def get_option(min=0, max=sys.maxsize):
    """TODO.

    Parameters
    ----------
    min : int, optional
        TODO.
    max : int, optional
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
                cprint('ERROR: invalid option: valid options are ' + str(min) + '-' + str(max), 'red')
        except:
            cprint('ERROR: invalid input: option must be a valid integer', 'red')
    print()
    return option

######################################################################
# Main Method
######################################################################

def main():
    """TODO."""
    
    print_welcome_banner()

    PEF_exp = exp.Experiment(input('Enter the experiment name: '))
    print("Beginning experiment '{name}'".format(name=PEF_exp.get_name()))
    
    end_exp = False
    option_range = PEF_exp.get_option_range()
    while (not end_exp):
        PEF_exp.display_options()
        option = get_option(min=option_range[0], max=option_range[1])
        end_exp = PEF_exp.process_option(option)

    return 0

if __name__ == '__main__':
    main()
