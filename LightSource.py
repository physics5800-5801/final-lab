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
# Class Definition
######################################################################

class Light_Source(object):
    """Class docstrings go here TODO."""
    def __init__(self, wavelength_nm, s_type="LED"):
        """Class method docstrings go here TODO."""
        self.__wavelength = wavelength_nm
        self.__source_type = s_type
        self.__source_df = None
        self.__stop_voltage = 0
        return
    
    def __str__(self):
        return ('Type: {0: >5},   λ: {1: >6.2f} nm,   V_s: {2: >5.3f} V'.format(self.__source_type, self.__wavelength, self.__stop_voltage))

    def get_type(self):
        return self.__source_type

    def get_wavelength(self):
        return self.__wavelength

    def get_data(self):
        return self.__source_df

    def get_stopping_volage(self):
        return self.__stop_volatge

    def get_color(self):
        λ = self.__wavelength
        if (λ >= 400 and λ < 450):
            return 'darkviolet'
        elif (λ >= 450 and λ < 500):
            return 'blue'
        elif (λ >= 500 and λ < 570):
            return 'forestgreen'
        elif (λ >= 570 and λ < 590):
            return 'gold'
        elif (λ >= 590 and λ < 610):
            return 'darkorange'
        elif (λ >= 610 and λ <= 700):
            return 'red'
        else:
            return 'black'

    def __get_max_voltage(self):
        λ = self.__wavelength
        if (λ >= 400 and λ < 450):
            return 1.8
        elif (λ >= 450 and λ < 500):
            return 1.5
        elif (λ >= 500 and λ < 570):
            return 1.2
        elif (λ >= 570 and λ < 590):
            return 1.0
        elif (λ >= 590 and λ < 610):
            return 0.8
        elif (λ >= 610 and λ <= 700):
            return 0.7
        else:
            return 2

    def __calc_stop_volage(self):
        retarding_voltage = np.array(self.__source_df['V_r'], dtype='float').reshape(-1,1)
        photocurrent = np.array(self.__source_df['I_φ'], dtype='float').reshape(-1,1)
        index = -1
        for i in range(photocurrent.size):
            if (photocurrent[i] >= 0):
                index = i
                break
        self.__stop_voltage = retarding_voltage[index][0]
        return

    def __create_source_df(source_data):
        source_df = pd.DataFrame([], columns=['V_r', 'I_ub', 'I_b', 'I_φ'])
        source_df['V_r'] = source_data[:,0]
        source_df['I_ub'] = source_data[:,1]
        source_df['I_b'] = source_data[:,2]
        source_df['I_φ'] = source_data[:,1] + source_data[:,2]
        self.__source_df = source_df.sort_values(by=['V_r'])
        return

    def collect_data(self):
        voltages = np.linspace(0, self.__get_max_voltage(), num=1500)
        np.random.shuffle(voltages)
        source_data = np.zeros((voltages.size,3))

        dark_current = 0
        while (True):
            try:
                dark_current = float(input('Enter the dark current value in V: '))
                break
            except:
                cprint('ERROR: invalid input: dark current must be a real number', 'red')

        input("Press ENTER to begin data collection...")
        for i in range(voltages.size):
            V_r = voltages[i]
            source_data[i,0] = V_r
            # DAQC2.setDAC(0,0,V_r)
            # V_p = DAQC2.getADC(0,0) - DAQC2.getADC(0,1)
            source_data[i,1] = V_p
            source_data[i,2] = dark_current
        self.__create_source_df(source_data)
        self.__calc_stop_volage()
        return

    def load_data_from_csv(self, filename):
        self.__source_df = pd.read_csv(filename)
        self.__calc_stop_volage()
        return

    def plot_data(self):
        retarding_voltage = np.array(self.__source_df['V_r'], dtype='float').reshape(-1,1)
        photocurrent = np.array(self.__source_df['I_φ'], dtype='float').reshape(-1,1)
        plt.scatter(retarding_voltage, photocurrent, color='black')
        plt.title('{0: .2f}nm {1:} Stopping Voltage'.format(self.__wavelength, self.__source_type), fontsize=18)
        plt.xlabel('Retarding Voltage (V)', fontsize=14)
        plt.ylabel('Photocurrent (µA)', fontsize=14)
        plt.gca().invert_yaxis()
        plt.grid()
        plt.show()
        return

    def save_data(self, out_dir='.'):
        path = out_dir + '/' + self.__source_type.lower() + '_' + str(round(self.__wavelength)) + 'nm.csv'
        self.__source_df.to_csv(path, encoding='utf-8', index=False)

        path = path.replace('.csv', '.jpg')
        retarding_voltage = np.array(self.__source_df['V_r'], dtype='float').reshape(-1,1)
        photocurrent = np.array(self.__source_df['I_φ'], dtype='float').reshape(-1,1)
        fig = plt.figure()
        plt.scatter(retarding_voltage, photocurrent, color='black')
        plt.title('{0: .2f}nm {1:} Stopping Voltage'.format(self.__wavelength, self.__source_type), fontsize=18)
        plt.xlabel('Retarding Voltage (V)', fontsize=14)
        plt.ylabel('Photocurrent (µA)', fontsize=14)
        plt.gca().invert_yaxis()
        plt.grid()
        fig.savefig(path, bbox_inches='tight', dpi=250)
        plt.close('all')
        return
