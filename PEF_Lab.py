#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Provides the script to run a photoelectric effect experiment.

This script sets up a new experiment to perform the photoelectric effect to estimate
the value of the elementary quantum of action, Plank's constant. The experiment allows
the user to collect or enter photocurrent data for various light sources and then
perform an estimation of Plank's constant and the work function of the photodiode that
is used given the data collected by the user. There are also options to save this data
and results to files for later viewing and analysis.
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
    """Prints the program welcome banner and instructions."""
    print('Welcome! Perform your own Photoelectric Effect experiment.')
    print('You will be asked to provide information about various light sources.')
    print("From this information, you will be able to approximate Plank's constant.")
    print("Select the 'Quit' option for the experiment when you are done.\n")
    return

def get_option(min=0, max=sys.maxsize):
    """Promts and gets a valid option for the experiment from the user.

    Parameters
    ----------
    min : int, optional
        The lower bound of the valid option range.
    max : int, optional
        The upper bound of the valid option range.

    Returns
    -------
    option : int
        A valid option for the experiment.
    """
    # Get option selection from user and validate
    option = -1
    while (option < min or option > max):
        # Check that option is a valid integer
        try:
            option = int(input('Select an option: '))
            # Check that option is in valid range
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
    """Sets up a new experiment to perform the photoelectric effect to estimate the value of the elementary
    quantum of action, Plank's constant. The experiment allows the user to collect or enter photocurrent
    data for various light sources and then perform an estimation of Plank's constant and the work function
    of the photodiode that is used given the data collected by the user. There are also options to save this
    data and results to files for later viewing and analysis..
    
    Returns
    -------
    value : int
        The values zero and indicate successful termination, anything else indicates unsuccessful termination.
    """
    # Print lab welcome message and instructions
    print_welcome_banner()
    # Create and begin new experiment 
    PEF_exp = exp.Experiment(input('Enter the experiment name: '))
    print("Beginning experiment '{name}'".format(name=PEF_exp.get_name()))
    # Get the valid range of options for the experiment
    option_range = PEF_exp.get_option_range()
    # Run photoelectric effect experiment until user decides to quit
    end_exp = False
    while (not end_exp):
        # Display experiment options
        PEF_exp.display_options()
        # Get option selection from user
        option = get_option(min=option_range[0], max=option_range[1])
        # Process selected option for the experiment
        end_exp = PEF_exp.process_option(option)
    return 0

"""Run the main method."""
if __name__ == '__main__':
    main()
