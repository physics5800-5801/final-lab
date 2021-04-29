#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Provides a Light_Source class for photoelectric effect experiments.

Light_Source holds the relevant type and wavelength (in nanometers) information for a
specific light source being used, and defines several methods to store collected data
pertaining to the light source (collect_data, plot_data, get_stopping_voltage, etc.).
"""

######################################################################
## Imports
######################################################################

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from termcolor import cprint
# import piplates.DAQC2plate as DAQC2

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
# Light_Source Class Definition
######################################################################

class Light_Source(object):
    """A class defining the data and behaviors of a light source for use in a photoelectric
    effect experiment.
    """

    def __init__(self, wavelength_nm, s_type="LED"):
        """Constructor for the Light_Source class.

        Parameters
        ----------
        wavelength_nm : float
            The wavelength (in nanometers) of the light source.
        s_type : string, optional
            The type of the light source.
        """
        self.__wavelength = wavelength_nm
        self.__source_type = s_type
        self.__source_df = None
        self.__stop_voltage = 0
        return
    
    def __str__(self):
        """Gets the string representation of the Light_Source object.

        Returns
        -------
        str_rep : string
            The string representation of the Light_Source object.
        """
        return ('Type: {0: >5},   λ: {1: >6.2f} nm,   V_s: {2: >5.3f} V'.format(self.__source_type, self.__wavelength, self.__stop_voltage))

    def get_type(self):
        """Gets the type of the light source.

        Returns
        -------
        type : string
            The type of the light source.
        """
        return self.__source_type

    def get_wavelength(self):
        """Gets the wavelength of the light source.

        Returns
        -------
        wavelength : float
            The wavelength (in nanometers) of the light source.
        """
        return self.__wavelength

    def get_data(self):
        """Gets the collected data for the light source.

        Returns
        -------
        data : DataFrame object
            The collected photocurent dataframe for the light source.
        """
        return self.__source_df

    def get_stopping_voltage(self):
        """Gets the stopping volatge for the light source.

        Returns
        -------
        V_s : float
            The stopping volatge (in volts) for the light source.
        """
        return self.__stop_voltage

    def __get_color(self):
        """Gets the plot color for the light source.

        Returns
        -------
        color : string
            The color (used for plotting) of the light source.
        """
        # Determine which color range the wavelength falls in
        if (self.__wavelength >= 400 and self.__wavelength < 450):          # color = purple
            return 'darkviolet'
        elif (self.__wavelength >= 450 and self.__wavelength < 500):        # color = blue
            return 'blue'
        elif (self.__wavelength >= 500 and self.__wavelength < 570):        # color = green
            return 'forestgreen'
        elif (self.__wavelength >= 570 and self.__wavelength < 590):        # color = yellow
            return 'gold'
        elif (self.__wavelength >= 590 and self.__wavelength < 610):        # color = orange
            return 'darkorange'
        elif (self.__wavelength >= 610 and self.__wavelength <= 700):       # color = reed
            return 'red'
        else:                                                               # color outside visible spectrum
            return 'black'

    def __get_max_voltage(self):
        """Gets the upper voltage bound for collecting for the light source.

        Returns
        -------
        max_voltage : float
            The upper voltage bound (in volts) for collecting data for the light source.
        """
        λ = self.__wavelength
        # Determine which color range the wavelength falls in
        if (λ >= 400 and λ < 450):              # color = purple
            return 1.8
        elif (λ >= 450 and λ < 500):            # color = blue
            return 1.5
        elif (λ >= 500 and λ < 570):            # color = green
            return 1.2
        elif (λ >= 570 and λ < 590):            # color = yellow
            return 1.0
        elif (λ >= 590 and λ < 610):            # color = orange
            return 0.8
        elif (λ >= 610 and λ <= 700):           # color = red
            return 0.7
        else:                                   # color outside visible spectrum
            return 2

    def __calc_stop_volage(self):
        """Calculates the stopping voltage for the light source based on the retarding voltage vs photocurrent
        data. Stopping voltage is estimated to be the voltage where teh photocurrent first dropps to zero.
        """
        # Extract retarding voltage and photocurrent data from dataframe
        retarding_voltage = np.array(self.__source_df['V_r'], dtype='float').reshape(-1,1)
        photocurrent = np.array(self.__source_df['I_φ'], dtype='float').reshape(-1,1)
        # Find first occurance of photocurrent dropping to zero
        index = -1
        for i in range(photocurrent.size):
            if (photocurrent[i] >= 0):
                index = i
                break
        # Set stopping voltage to voltage where photocurrent first dropped to zero
        self.__stop_voltage = retarding_voltage[index][0]
        return

    def __create_source_df(self, source_data):
        """Loads the collected retarding voltage vs photocurrent data into a dataframe for the light source.

        Parameters
        ----------
        source_data : ndarray
            The collected photocurent data for the light source.
        """
        # Create empty dataframe with columns for retarding volatge, the photocurrent when the light
        # source is unblocked and blocked, and the effective photocurrent.
        source_df = pd.DataFrame([], columns=['V_r', 'I_ub', 'I_b', 'I_φ'])
        # Load collected data into dataframe
        source_df['V_r'] = source_data[:,0]
        source_df['I_ub'] = source_data[:,1]
        source_df['I_b'] = source_data[:,2]
        source_df['I_φ'] = source_data[:,1] + source_data[:,2]
        # Sort dataframe by ordering based on increasing retarding voltage
        self.__source_df = source_df.sort_values(by=['V_r'])
        return

    def collect_data(self):
        """Collect retarding voltage vs photocurrent data for the light source into a dataframe and determine
        the stopping voltage for the light source.
        """
        # Get retarging voltages to take samples over and randomize sample to avoid error in collection
        voltages = np.linspace(0, self.__get_max_voltage(), num=1500)
        np.random.shuffle(voltages)
        # Get dark current value (photocurrent when blocked) from user
        dark_current = 0
        while (True):
            try:
                dark_current = float(input('Enter the dark current value in V: '))
                break
            except:
                cprint('ERROR: invalid input: dark current must be a real number', 'red')
        # Collect photocurrent data over all retarding volatge samples
        source_data = np.zeros((voltages.size,3))
        input("Press ENTER to begin data collection...")
        for i in range(voltages.size):
            V_r = voltages[i]
            source_data[i,0] = V_r
            # Set retarding voltage to supply to photodiode
            # DAQC2.setDAC(0,0,V_r)
            # Measure resulting photocurrent
            # V_p = DAQC2.getADC(0,0) - DAQC2.getADC(0,1)
            source_data[i,1] = V_p
            source_data[i,2] = dark_current
        # Store data in dataframe
        self.__create_source_df(source_data)
        # Estimate stopping voltage for light source
        self.__calc_stop_volage()
        return

    def load_data_from_csv(self, filename):
        """Load light source dataframe with data from existing csv file and determine the stopping voltage
        for the light source.

        Parameters
        ----------
        filename : string
            The name of the file from which to load data.
        """
        # Load data from csv file into dataframe
        self.__source_df = pd.read_csv(filename)
        # Estimate stopping voltage for light source
        self.__calc_stop_volage()
        return

    def plot_data(self):
        """Graph the collected light source data and calculated stopping voltage."""
        # Extract retarding voltage and photocurrent data from dataframe
        retarding_voltage = np.array(self.__source_df['V_r'], dtype='float').reshape(-1,1)
        photocurrent = np.array(self.__source_df['I_φ'], dtype='float').reshape(-1,1)
        # Plot retarding voltage vs photocurrent data
        plt.scatter(retarding_voltage, photocurrent, color='black')
        # Plot vertical line for stopping voltage
        label = 'V_s = {:.4f}'.format(self.__stop_voltage)
        plt.axvline(x=self.__stop_voltage, color=self.__get_color(), label=label)
        # Add labels and other details to graph
        plt.title('{0:.2f}nm {1:} Stopping Voltage'.format(self.__wavelength, self.__source_type), fontsize=18)
        plt.xlabel('Retarding Voltage (V)', fontsize=14)
        plt.ylabel('Photocurrent (µA)', fontsize=14)
        plt.gca().invert_yaxis()
        plt.grid()
        plt.legend(loc='lower left')
        # Show the plot
        plt.show()
        return

    def save_data(self, out_dir='.'):
        """Save the collected light source data and calculated stopping voltage to files.

        Parameters
        ----------
        out_dir : string, optional
            The name of the directory to save the data to.
        """
        # Get path for file to save light source dataframe to
        path = out_dir + '/' + self.__source_type.lower() + '_' + str(round(self.__wavelength)) + 'nm.csv'
        self.__source_df.to_csv(path, encoding='utf-8', index=False)
        # Get path for file to save light source graph to
        path = path.replace('.csv', '.jpg')
        # Extract retarding voltage and photocurrent data from dataframe
        retarding_voltage = np.array(self.__source_df['V_r'], dtype='float').reshape(-1,1)
        photocurrent = np.array(self.__source_df['I_φ'], dtype='float').reshape(-1,1)
        # Create figure to save plot to
        fig = plt.figure()
        # Plot retarding voltage vs photocurrent data
        plt.scatter(retarding_voltage, photocurrent, color='black')
        # Plot vertical line for stopping voltage
        label = 'V_s = {:.4f}'.format(self.__stop_voltage)
        plt.axvline(x=self.__stop_voltage, color=self.__get_color(), label=label) 
        # Add labels and other details to graph
        plt.title('{0:.2f}nm {1:} Stopping Voltage'.format(self.__wavelength, self.__source_type), fontsize=18)
        plt.xlabel('Retarding Voltage (V)', fontsize=14)
        plt.ylabel('Photocurrent (µA)', fontsize=14)
        plt.gca().invert_yaxis()
        plt.grid()
        plt.legend(loc='lower left')
        # Save and close the plot
        fig.savefig(path, bbox_inches='tight', dpi=250)
        plt.close('all')
        return
