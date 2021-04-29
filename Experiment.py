#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Provides an Experiment class for photoelectric effect experiments.

Experiment holds a sequence of Light_Sources and relevant constants, and defines several
methods to operate and run the experiment (display_options, process_option, etc.). Some
of the various options include adding, removing, updating, displaying, and saving
Light_Source data and displaying and saving the final results and estimations from the
experiment. The final results include estimations of Plank's constant and the work
function for a Cesium-Antimony photodiode.
"""

######################################################################
## Imports
######################################################################

import re, unicodedata
import os, sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
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
# Experiment Class Definition
######################################################################

class Experiment(object):
    """A class defining the data and behaviors of a photoelectric effect experiment."""
    
    __PLANKS_CONSTANT = 6.62607015e-34          # the accepted value for planks constant
    __WF_CESIUM_ANTIMONY = (1.43,1.59)          # the accepted value for the work function for cesium-antimony
    __SPEED_LIGHT = 299792458                   # the accepted value for the speed of light
    __N_AIR = 1.000293                          # the accepted value for the refractive index of air (at room temp)
    __ELECTRON_CHARGE = -1.602176634e-19        # the accepted value for the charge of an electron

    def __init__(self, name="unnamed"):
        """Constructor for the Experiment class.

        Parameters
        ----------
        name : string, optional
            The name given to the experiment.
        """
        slug_name = self.__slugify(name)        # get properly formatted name
        self.__name = 'unnamed' if (slug_name == '') else slug_name
        self.__datalog = []
        self.__energy_df = None
        self.__plank = 0
        self.__work_func = 0
        return

    def __slugify(self, value, allow_unicode=False):
        """Taken from https://github.com/django/django/blob/master/django/utils/text.py.
        Convert to ASCII if 'allow_unicode' is False. Convert spaces or repeated dashes
        to single dashes. Remove characters that aren't alphanumerics, underscores, or
        hyphens. Convert to lowercase. Also strip leading and trailing whitespace,
        dashes, and underscores.

        Parameters
        ----------
        value : string
            The value to convert to a properly formatted filename.
        allow_unicode : bool, optional
            Whether of not to allow unicode in the filename.

        Returns
        -------
        slug_value : string
            The properly formatted filename for the object.
        """
        value = str(value)
        if allow_unicode:
            value = unicodedata.normalize('NFKC', value)
        else:
            value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
        value = re.sub(r'[^\w\s-]', '', value.lower())
        return re.sub(r'[-\s]+', '-', value).strip('-_')
    
    def get_name(self):
        """Gets the name given to the experiment.

        Returns
        -------
        name : string
            The name given to the experiment.
        """
        return self.__name

    def get_option_range(self):
        """Gets the range of valid options for the experiment.

        Returns
        -------
        option_range : tuple(int)
            The lower and upper bounds of the tange of valid options for the experiment.
        """
        option_keys = self.__options.keys()
        return (min(option_keys), max(option_keys))

    def __get_plank_error(self):
        """Calculates the percent error in the estimate of Plank's constant for the experiment.

        Returns
        -------
        error : float
            The percent error in the estimate of Plank's constant.
        """
        return (abs((self.__plank - self.__PLANKS_CONSTANT) / self.__PLANKS_CONSTANT) * 100)
    
    def __create_energy_df(self):
        """Loads the collected wavelength vs source max energy data into a dataframe for the experiment."""
        # Retrieve the wavelength vs stopping voltage for each light source
        source_data = np.array([[entry.get_wavelength(), entry.get_stopping_voltage()] for entry in self.__datalog])
        # Create empty dataframe with columns for source wavelength, frequency, stopping voltage, and max energy.
        energy_df = pd.DataFrame([], columns=['λ', 'ν', 'V_s', 'E'])
        # Load collected data into dataframe
        energy_df['λ'] = (source_data[:,0] * 1e-09)
        energy_df['ν'] = self.__SPEED_LIGHT / (self.__N_AIR * energy_df['λ'])
        energy_df['V_s'] = source_data[:,1]
        energy_df['E'] = abs(self.__ELECTRON_CHARGE) * energy_df['V_s']
        # Sort dataframe by ordering based on increasing wavelength
        self.__energy_df = energy_df.sort_values(by=['λ'])
        return

    def __get_color(self, wavelength_nm):
        """Gets the plot color for the light source..

        Parameters
        ----------
        wavelength_nm : float
            The wavelength (in nanometers) of a light source.

        Returns
        -------
        color : string
            The color (used for plotting) of the light source.
        """
        # Determine which color range the wavelength falls in
        if (wavelength_nm >= 400 and wavelength_nm < 450):          # color = purple
            return 'darkviolet'
        elif (wavelength_nm >= 450 and wavelength_nm < 500):        # color = blue
            return 'blue'
        elif (wavelength_nm >= 500 and wavelength_nm < 570):        # color = green
            return 'forestgreen'
        elif (wavelength_nm >= 570 and wavelength_nm < 590):        # color = yellow
            return 'gold'
        elif (wavelength_nm >= 590 and wavelength_nm < 610):        # color = orange
            return 'darkorange'
        elif (wavelength_nm >= 610 and wavelength_nm <= 700):       # color = red
            return 'red'
        else:                                                       # color outside visible spectrum
            return 'black'

    def __plot_energy_data(self, margin=1e-20, save=False):
        """Graph the collected light source energy data for the experiment and perform a linear regression
        to estimate the values of Plank's constant and the photodiode work function.

        Parameters
        ----------
        margin : float, optional
            The margin width for the plot.
        save : bool, optional
            Whether or not to save the plot to a file.
        """
        # Extract frequency and energy data and plot color from dataframe
        frequency = np.array(self.__energy_df['ν'], dtype='float').reshape(-1,1)
        energy = np.array(self.__energy_df['E'], dtype='float').reshape(-1,1)
        source_colors = [self.__get_color(λ/1e-09) for λ in self.__energy_df['λ']]
        # Perform linear regression of energy data for which to estimate Plank's constant and work function
        energy_model = LinearRegression()
        energy_model.fit(frequency, energy)
        weights = np.array([energy_model.intercept_, energy_model.coef_], dtype=object).flatten()
        Y_pred = weights[1]*frequency + weights[0]
        # Estimate Plank's constant and work function
        self.__work_func = weights[0] / self.__ELECTRON_CHARGE
        self.__plank = weights[1]
        # Plot frequency vs energy data
        if (save): fig = plt.figure()
        plt.scatter(frequency, energy, color=source_colors)
        # Plot regression line
        label = 'KE = ({0:.4e})f {1:+.4e}'.format(weights[1], weights[0])
        plt.plot([min(frequency), max(frequency)], [min(Y_pred), max(Y_pred)], label=label, linestyle='dashed', color='darkgray')
        # # Add labels and other details to graph
        plt.title("Determining Plank's Constant", fontsize=18)
        plt.xlabel('Frequency (Hz)', fontsize=14)
        plt.ylabel('Required Work (J)', fontsize=14)
        plt_range = (min(min(energy), min(Y_pred)),max(max(energy), max(Y_pred)))
        plt.ylim(plt_range[0]-margin, plt_range[1]+margin)
        plt.grid()
        plt.legend(loc='upper left')
        # Save or show the plot
        if (save):
            path = './' + self.__name + '/' + 'plank_estimate.jpg'
            fig.savefig(path, bbox_inches='tight', dpi=250)
            plt.close('all')
        else:
            plt.show()
        return

    def __print_report(self, save=False):
        """Either displays a report of the current experiment estimates and results to the user or
        saves it to a file.

        Parameters
        ----------
        save : bool, optional
            Whether or not to save the results to a file.
        """
        # Save standard output stream
        stdout_fileno = sys.stdout
        try:
            # Create file to write report to is it should be saved
            if (save):
                # Get or create directory to save report to
                out_dir = './' + self.__name
                if (not os.path.exists(out_dir)):
                    os.mkdir(out_dir)
                # Create file to save report to
                path = out_dir + '/' + 'report.txt'
                sys.stdout = open(path, 'w', encoding='utf-8')
            # Print or save experiment datalog
            self.__display_log()
            # Print or save experiment estimates and results
            print('\n-------------------- Report --------------------')
            print('Cesium-Antimony Work Function (Φ):')
            print('  actual   = {0}-{1} eV'.format(self.__WF_CESIUM_ANTIMONY[0], self.__WF_CESIUM_ANTIMONY[1]))
            print('  estimate = {:.5f} eV'.format(self.__work_func))
            print("Plank's Constant (h):")
            print('  actual   = {:.8e} J⋅s'.format(self.__PLANKS_CONSTANT))
            print('  estimate = {:.8e} J⋅s'.format(self.__plank))
            print('  % error  = {:.4f}%'.format(self.__get_plank_error()))
            # Close file and restore standard output stream
            if (save):
                sys.stdout.close()
                sys.stdout = stdout_fileno
        except:
            sys.stdout.close()
            sys.stdout = stdout_fileno
            raise Exception('__print_report: fileIO exception')      
        return

    def display_options(self):
        """
        Displays the menu of valid experiment options that can be performed.
        """
        # Print experiment options menu
        print('\n------------------------- EXPERIMENT OPTIONS -------------------------')
        for i in range(len(self.__options)):
            # Print description of current option in options list
            print('{indx: >4}. {desc}'.format(indx=i, desc=self.__options[i][1]))
        print('----------------------------------------------------------------------')
        return

    def process_option(self, option):
        """Processes the selected experiment option for the current experiment.

        Parameters
        ----------
        option : int
            The selected experiment option to perform.

        Returns
        -------
        quit : bool
            Whether or not to quit the experiment.
        """
        print('OPTION {0}: {1}'.format(option, self.__options[option][1]))
        return self.__options[option][0](self)
    
    def __quit(self):
        """Prompts the user if they would like to end the experiment and quits the current experiment if
        they choose to do so.

        Returns
        -------
        quit : bool
            Whether or not to quit the experiment.
        """
        # Get confirmation to continue from user
        print('Warning - Unsaved data will be lost.')
        confirmation = input('Would you like to proceed (y/n)?: ').lower()
        while (confirmation != 'y' and confirmation != 'n'):
            cprint("ERROR: invalid input: please enter either 'y' or 'n'", 'red')
            confirmation = input('Would you like to proceed (y/n)?: ').lower()
        # Quit experiment if user confirmed
        return (True if (confirmation == 'y') else False)

    def __add_log_entry(self):
        """Prompts the user to collect or load data for a light source entry and adds it to the current
        datalog for the experiment and displays teh data.
        """
        # Get source type from user
        source_type = input('Is this an LED or a Laser?: ').upper()
        while (source_type != 'LED' and source_type != 'LASER'):
            cprint("ERROR: invalid input: please enter either 'LED' or 'Laser'", 'red')
            source_type = input('Is this an LED or a Laser?: ').upper()
        if (source_type != 'LED'): source_type = source_type.capitalize()
        # Get source wavelength (in nanometers) from user
        wavelength_nm = 0
        while (wavelength_nm <= 0):
            try:
                wavelength_nm = float(input('Enter the {} wavelength in nm: '.format(source_type)))
                if (wavelength_nm <= 0): cprint('ERROR: invalid input: wavelength must be a positive real number', 'red')
            except:
                cprint('ERROR: invalid input: wavelength must be a positive real number', 'red')
        # Create light source entry from based on entered user specifications
        entry = source.Light_Source(wavelength_nm, source_type)
        # Get load file response from user
        from_file = input('Load data from csv file (y/n)?: ').lower()
        while (from_file != 'y' and from_file != 'n'):
            cprint("ERROR: invalid input: please enter either 'y' or 'n'", 'red')
            from_file = input('Load data from csv file (y/n)?: ').lower()
        # Load data from file if available, otherwise collect data manually
        if (from_file == 'y'):
            try:
                # Load data from existing csv file
                entry.load_data_from_csv(input('Enter csv file path: '))
            except:
                cprint('ERROR: read_csv: unable to load file', 'red')
                return
        else:
            # Collect data manually
            entry.collect_data()
        # Add light source entry to datalog
        print('[+]Added entry:')
        print('->', entry)
        self.__datalog += [entry]
        # Plot the added light source data
        entry.plot_data()
        return

    def __remove_log_entry(self):
        """Prompts the user for a entry to remove from the current experiment datalog and removes the entry
        from the datalog if it was a valid entry.
        """
        # Check that there is at least 1 entry in the datalog
        if (len(self.__datalog) > 0):
            # Print curernt experiment datalog
            self.__display_log()
            print('Warning - This action cannot be undone')
            try:
                # Get entry to remove from experiment datalog
                indx = int(input('Select the entry to remove: '))
                # Remove selected entry if valid
                if (indx >= 0 and indx < len(self.__datalog)):
                    # Remove entry from datalog
                    entry = self.__datalog.pop(indx)
                    # Print removed entry
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
        """Prompts the user for a entry to update from the current experiment datalog and updates the entry
        from the datalog if it was a valid entry.
        """
        # Check that there is at least 1 entry in the datalog
        if (len(self.__datalog) > 0):
            # Print curernt experiment datalog
            self.__display_log()
            print('Warning - This operation will overwrite existing data')
            try:
                # Get entry to update from experiment datalog
                indx = int(input('Select the entry to update: '))
                # Update selected entry if valid
                if (indx >= 0 and indx < len(self.__datalog)):
                    # Remove entry from datalog
                    entry = self.__datalog.pop(indx)
                    print('{i: >2}. '.format(i=indx), entry)
                    # Create new light source entry from based on selected entry to update
                    new_entry = source.Light_Source(entry.get_wavelength(), entry.get_type())
                    # Get load file response from user
                    from_file = input('Load data from csv file (y/n)?: ').lower()
                    while (from_file != 'y' and from_file != 'n'):
                        cprint("ERROR: invalid input: please enter either 'y' or 'n'", 'red')
                        from_file = input('Load data from csv file (y/n)?: ').lower()
                    # Load data from file if available, otherwise collect data manually
                    if (from_file == 'y'):
                        try:
                            # Load data from existing csv file
                            new_entry.load_data_from_csv(input('Enter csv file path: '))
                        except:
                            cprint('ERROR: read_csv: unable to load file', 'red')
                            return
                    else:
                        # Collect data manually
                        new_entry.collect_data()
                    # Add updated light source entry to datalog
                    print('[+]Updated entry:')
                    print('->', new_entry)
                    self.__datalog += [new_entry]
                    # Plot the updated light source data
                    new_entry.plot_data()
                else:
                    cprint('ERROR: invalid entry: no entries were updated', 'red')
            except:
                cprint('ERROR: invalid entry: no entries were updated', 'red')
        else:
            print('[+]The datalog is currently empty')
        return

    def __display_log(self):
        """Displays the current experiment datalog.
        """
        # Check that there is at least 1 entry in the datalog
        log_size = len(self.__datalog)
        if (log_size > 0):
            # Print curernt experiment datalog
            print('--------------- Datalog for {name} ---------------'.format(name=self.__name))
            for i in range(log_size):
                # Print current entry in experiment datalog
                print('{indx: >2}. '.format(indx=i), self.__datalog[i])
        else:
            print('[+]The datalog is currently empty')
        return

    def __view_log_entry(self):
        """Prompts the user for a entry to view from the current experiment datalog and displays the data and
        plot for the entry if it was a valid entry.
        """
        # Check that there is at least 1 entry in the datalog
        log_size = len(self.__datalog)
        if (log_size > 0):
            # Print curernt experiment datalog
            self.__display_log()
            try:
                # Get entry to view from experiment datalog
                indx = int(input('Select the entry to view: '))
                # View selected entry if valid
                if (indx >= 0 and indx < log_size):
                    # Print the selected entry
                    entry = self.__datalog[indx]
                    print('{i: >2}. '.format(i=indx), entry, '\n')
                    # Print the data for the selected entry
                    print(entry.get_data())
                    # Display data plot for the selected entry
                    entry.plot_data()
                else:
                    cprint('ERROR: invalid entry: unable to view entry', 'red')
            except:
                cprint('ERROR: invalid entry: unable to view entry', 'red')
        else:
            print('[+]The datalog is currently empty')
        return

    def __save_log(self):
        """Saves the dataframe and plot of each entry in the current experiment datalog to files."""
        # Check that there is at least 1 entry in the datalog
        log_size = len(self.__datalog)
        if (log_size > 0):
            # Get confirmation to continue from user
            print('Warning - This action may overwrite existing save files')
            confirmation = input('Would you like to proceed (y/n)?: ').lower()
            while (confirmation != 'y' and confirmation != 'n'):
                cprint("ERROR: invalid input: please enter either 'y' or 'n'", 'red')
                confirmation = input('Would you like to proceed (y/n)?: ').lower()
            # Save current datalog to file if user confirmed
            if (confirmation == 'y'):
                try:
                    # Get or create directory to save datalog to
                    out_dir = './' + self.__name
                    if (not os.path.exists(out_dir)):
                        os.mkdir(out_dir)
                    # Save data for each entry in datalog to csv files
                    for i in range(log_size):
                        # Save current entry in datalog to file
                        self.__datalog[i].save_data(out_dir)
                    print('[+]The datalog has been saved')
                except:
                    cprint('ERROR: save_log: unable to save data to files', 'red')
        else:
            print('[+]The datalog is currently empty')
        return

    def __display_results(self):
        """Displays the plot of the frequency vs energy data with fitted linear regressiona and prints the
        current estimates and accuracy results for the experiment.
        """
        # Check that there is at least 1 entry in the datalog
        if (len(self.__datalog) > 0):
            # Create wavelength vs energy dataframe from each light source entry in datalog
            self.__create_energy_df()
            # Plot current experiment results and regression line
            self.__plot_energy_data()
            # Print the current estimates and accuracy results for the experiment
            self.__print_report()
        else:
            print('[+]The datalog is currently empty')
        return

    def __save_results(self):
        """Saves the plot of the frequency vs energy data with fitted linear regressiona and the
        current estimates and accuracy results for the experiment to files.
        """
        # Check that there is at least 1 entry in the datalog
        if (len(self.__datalog) > 0):
            # Get confirmation to continue from user
            print('Warning - This action may overwrite existing save files')
            confirmation = input('Would you like to proceed (y/n)?: ').lower()
            while (confirmation != 'y' and confirmation != 'n'):
                cprint("ERROR: invalid input: please enter either 'y' or 'n'", 'red')
                confirmation = input('Would you like to proceed (y/n)?: ').lower()
            # Save results to file if user confirmed
            if (confirmation == 'y'):
                try:
                    # Get or create directory to save results to
                    out_dir = './' + self.__name
                    if (not os.path.exists(out_dir)):
                        os.mkdir(out_dir)
                    # Create wavelength vs energy dataframe from each light source entry in datalog
                    self.__create_energy_df()
                    # Create file to save wavelength vs energy dataframe to
                    path = out_dir + '/' + 'source_energies.csv'
                    self.__energy_df.to_csv(path, encoding='utf-8', index=False)
                    # Save plot of current experiment results and regression line to file
                    self.__plot_energy_data(save=True)
                    # Save current estimates and accuracy results for the experiment to file
                    self.__print_report(save=True)
                    print('[+]The results have been saved')
                except:
                    cprint('ERROR: save_results: unable to save results to file', 'red')
        else:
            print('[+]The datalog is currently empty')
        return

    def __clear_log(self):
        """Clears current experiment datalog of all entries.
        """
        # Check that there is at least 1 entry in the datalog
        if (len(self.__datalog) > 0):
            # Get confirmation to continue from user
            print('Warning - This action cannot be undone')
            confirmation = input('Would you like to proceed (y/n)?: ').lower()
            while (confirmation != 'y' and confirmation != 'n'):
                cprint("ERROR: invalid input: please enter either 'y' or 'n'", 'red')
                confirmation = input('Would you like to proceed (y/n)?: ').lower()
            # Clear datalog entries if user confirmed
            if (confirmation == 'y'):
                self.__datalog.clear()
                print('[+]The datalog has been cleared')
        else:
            print('[+]The datalog is already empty')
        return

    # Mapping of valid experiment options and their descriptions
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
