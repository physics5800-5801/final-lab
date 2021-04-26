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

import re
import unicodedata
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from termcolor import cprint
import LightSource as source

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
# Class Definition
######################################################################

class Experiment(object):
    """Class docstrings go here TODO."""
    __PLANKS_CONSTANT = 6.62607015e-34
    __SPEED_LIGHT = 299792458
    __N_AIR = 1.000293
    __ELECTRON_CHARGE = -1.602176634e-19

    def __init__(self, name="unnamed"):
        """Class method docstrings go here TODO."""
        slug_name = self.__slugify(name)
        self.__name = 'unnamed' if (slug_name == '') else slug_name
        self.__datalog = []
        self.__energy_df = None
        self.__plank = 0
        self.__work_func = 0
        return

    def __slugify(self, value, allow_unicode=False):
        """Taken from https://github.com/django/django/blob/master/django/utils/text.py.
        Convert to ASCII if 'allow_unicode' is False. Convert spaces or repeated
        dashes to single dashes. Remove characters that aren't alphanumerics,
        underscores, or hyphens. Convert to lowercase. Also strip leading and
        trailing whitespace, dashes, and underscores.

        Parameters
        ----------
        value : string
            TODO.
        allow_unicode : bool, optional
            TODO.

        Returns
        -------
        slug_value : string
            TODO.
        """

        value = str(value)
        if allow_unicode:
            value = unicodedata.normalize('NFKC', value)
        else:
            value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
        value = re.sub(r'[^\w\s-]', '', value.lower())
        return re.sub(r'[-\s]+', '-', value).strip('-_')
    
    def get_name(self):
        return self.__name

    def get_option_range(self):
        option_keys = self.__options.keys()
        return (min(option_keys), max(option_keys))
    
    def __create_energy_df(self):
        source_data = np.array([[entry.get_wavelength(), entry.get_stopping_voltage()] for entry in self.__datalog])
        energy_df = pd.DataFrame([], columns=['λ', 'ν', 'V_s', 'E'])
        energy_df['λ'] = (source_data[:,0] * 1e-09)
        energy_df['ν'] = self.__SPEED_LIGHT / (self.__N_AIR * energy_df['λ'])
        energy_df['V_s'] = source_data[:,1]
        energy_df['E'] = abs(self.__ELECTRON_CHARGE) * energy_df['V_s']
        self.__energy_df = energy_df.sort_values(by=['λ'])
        return

    def display_options(self):
        """
        TODO.
        """

        print('\n------------------------- EXPERIMENT OPTIONS -------------------------')
        for i in range(len(self.__options)):
            print('{indx: >4}. {desc}'.format(indx=i, desc=self.__options[i][1]))
        print('----------------------------------------------------------------------')
        return

    def process_option(self, option):
        print('OPTION ' + str(option) + ': ' +self.__options[option][1])
        return self.__options[option][0](self)
    
    def __quit(self):
        print('Warning - Unsaved data will be lost.')
        confirmation = input('Would you like to proceed (y/n)?: ').lower()
        while (confirmation != 'y' and confirmation != 'n'):
            cprint("ERROR: invalid input: please enter either 'y' or 'n'", 'red')
            confirmation = input('Would you like to proceed (y/n)?: ').lower()
        return (True if (confirmation == 'y') else False)

    def __add_log_entry(self):
        source_type = input('Is this an LED or a Laser?: ').upper()
        while (source_type != 'LED' and source_type != 'LASER'):
            cprint("ERROR: invalid input: please enter either 'LED' or 'Laser'", 'red')
            source_type = input('Is this an LED or a Laser?: ').upper()
        if (source_type != 'LED'): source_type = source_type.capitalize()
        wavelength_nm = 0
        while (wavelength_nm <= 0):
            try:
                wavelength_nm = float(input('Enter the {} wavelength in nm: '.format(source_type)))
                if (wavelength_nm <= 0): cprint('ERROR: invalid input: wavelength must be a positive real number', 'red')
            except:
                cprint('ERROR: invalid input: wavelength must be a positive real number', 'red')
        
        entry = source.Light_Source(wavelength_nm, source_type)
        from_file = input('Load data from csv file (y/n)?: ').lower()
        while (from_file != 'y' and from_file != 'n'):
            cprint("ERROR: invalid input: please enter either 'y' or 'n'", 'red')
            from_file = input('Load data from csv file (y/n)?: ').lower()
        if (from_file == 'y'):
            try:
                entry.load_data_from_csv(input('Enter csv file path: '))
            except:
                cprint('ERROR: read_csv: unable to load file', 'red')
                return
        else:
            entry.collect_data()
        print('[+]Added entry:')
        print('->', entry)
        entry.plot_data()
        self.__datalog += [entry]
        return

    def __remove_log_entry(self):
        if (len(self.__datalog) > 0):
            self.__display_log()
            print('Warning - This action cannot be undone')
            try:
                indx = int(input('Select the entry to remove: '))
                if (indx >= 0 and indx < len(self.__datalog)):
                    entry = self.__datalog.pop(indx)
                    print('[+]Removed entry:')
                    print('->', entry)
                else:
                    cprint('ERROR: invalid entry: no entries were removed', 'red')
            except:
                cprint('ERROR: invalid entry: no entries were removed', 'red')
        else:
            print('[+]The datalog is already empty')
        return

    def __update_log_entry(self):
        if (len(self.__datalog) > 0):
            self.__display_log()
            print('Warning - This operation will overwrite existing data')
            try:
                indx = int(input('Select the entry to update: '))
                if (indx >= 0 and indx < len(self.__datalog)):
                    entry = self.__datalog.pop(indx)
                    print('{i: >2}. '.format(i=indx), entry)
                    new_entry = source.Light_Source(entry.get_wavelength(), entry.get_type())
                    from_file = input('Load data from csv file (y/n)?: ').lower()
                    while (from_file != 'y' and from_file != 'n'):
                        cprint("ERROR: invalid input: please enter either 'y' or 'n'", 'red')
                        from_file = input('Load data from csv file (y/n)?: ').lower()
                    if (from_file == 'y'):
                        try:
                            new_entry.load_data_from_csv(input('Enter csv file path: '))
                        except:
                            cprint('ERROR: read_csv: unable to load file', 'red')
                            return
                    else:
                        new_entry.collect_data()
                    print('[+]Updated entry:')
                    print('->', new_entry)
                    new_entry.plot_data()
                    self.__datalog += [new_entry]
                else:
                    cprint('ERROR: invalid entry: no entries were updated', 'red')
            except:
                cprint('ERROR: invalid entry: no entries were updated', 'red')
        else:
            print('[+]The datalog is currently empty')
        return

    def __display_log(self):
        log_size = len(self.__datalog)
        if (log_size > 0):
            print('--------------- Datalog for {name} ---------------'.format(name=self.__name))
            for i in range(log_size):
                print('{indx: >2}. '.format(indx=i), self.__datalog[i])
        else:
            print('[+]The datalog is currently empty')
        return

    def __view_log_entry(self):
        log_size = len(self.__datalog)
        if (log_size > 0):
            self.__display_log()
            try:
                indx = int(input('Select the entry to view: '))
                if (indx >= 0 and indx < len(self.__datalog)):
                    entry = self.__datalog[indx]
                    print('{i: >2}. '.format(i=indx), entry, '\n')
                    print(entry.get_data())
                    entry.plot_data()
                else:
                    cprint('ERROR: invalid entry: unable to view entry', 'red')
            except:
                cprint('ERROR: invalid entry: unable to view entry', 'red')
        else:
            print('[+]The datalog is currently empty')
        return

    def __save_log(self):
        if (len(self.__datalog) > 0):
            print('Warning - This action may overwrite existing save files')
            confirmation = input('Would you like to proceed (y/n)?: ').lower()
            while (confirmation != 'y' and confirmation != 'n'):
                cprint("ERROR: invalid input: please enter either 'y' or 'n'", 'red')
                confirmation = input('Would you like to proceed (y/n)?: ').lower()
            if (confirmation == 'y'):
                try:
                    out_dir = './' + self.__name
                    if (not os.path.exists(out_dir)):
                        os.mkdir(out_dir)
                    for i in range(len(self.__datalog)):
                        self.__datalog[i].save_data(out_dir)
                    print('[+]The datalog has been saved')
                except:
                    cprint('ERROR: save_log: unable to save data to files', 'red')
        else:
            print('[+]The datalog is currently empty')
        return

    def __display_results(self):
        if (len(self.__datalog) > 0):
            self.__create_energy_df()
        else:
            print('[+]The datalog is already empty')
        return

    def __save_results(self):
        if (len(self.__datalog) > 0):
            x = 0
        else:
            print('[+]The datalog is already empty')
        return

    def __clear_log(self):
        if (len(self.__datalog) > 0):
            print('Warning - This action cannot be undone')
            confirmation = input('Would you like to proceed (y/n)?: ').lower()
            while (confirmation != 'y' and confirmation != 'n'):
                cprint("ERROR: invalid input: please enter either 'y' or 'n'", 'red')
                confirmation = input('Would you like to proceed (y/n)?: ').lower()
            if (confirmation == 'y'):
                self.__datalog.clear()
                print('[+]The datalog has been cleared')
        else:
            print('[+]The datalog is already empty')
        return

    __options = {0: (__quit, 'Quit experiment'),
                 1: (__add_log_entry, 'Add entry to datalog'),
                 2: (__remove_log_entry, 'Remove entry from datalog'),
                 3: (__update_log_entry, 'Update datalog entry'),
                 4: (__display_log, 'Display current datalog'),
                 5: (__view_log_entry, 'View datalog entry'),
                 6: (__save_log, 'Save datalog entries to files'),
                 7: (__display_results, 'Display estimate results'),
                 8: (__save_results, 'Save results'),
                 9: (__clear_log, 'Clear datalog')}
