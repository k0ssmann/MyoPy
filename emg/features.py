#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 25 12:45:45 2022

@author: adriank
"""

import numpy as np
import pandas as pd
import scipy.io
from scipy.stats import skew 
from scipy.stats import kurtosis
import pickle 
from scipy import stats

class features:
    
    def __init__(self, epochs, features=None):
        
        self._feature_dict = {
                'IEMG': IEMG,
                'MAV': MAV,
                'MMAV1': MMAV1,
                'MMAV2': MMAV2,
                'VAR': VAR,
                'SD': SD,
                #'KURT': Kurt,
                #'SKEW': Skew,
                'SSI': SSI,
                'RMS': RMS,
                'AAC': AAC,
                'WL': WL,                
                }
        
        self._epochs = epochs
        self._features = features
        
        if self._features is None:
            self._features = self._feature_dict.keys()
        
        if isinstance(self._features, str):
            self._features = [features]
        

        self._events = self._epochs.events
        
        self._values, self._labels, self._classes = self.calculate()
    
    def find_emg(self, epochs):
        chs = epochs.info['chs']
        
        indices = []

        for i, d in enumerate(chs):
            if d.get('ch_type') == 'EMG':
                indices.append(i)
        
        
        return len(indices)
        
    
    def calculate(self):
        
        events = np.unique(self._events[:,1])
        n_emg = self.find_emg(self._epochs)
        labels = sorted([feature + str(i) for i in range(1, n_emg+1) for feature in self._features])
        features = []
        classes = []
        
        
        for e, event in enumerate(events):
            
            mask = np.isin(self._events[:, 1], event)
            classes.append(self._events[mask, 1])
            event_features = []
            
            for f, feature in enumerate(self._features):
                data = self._epochs._data[mask]
                event_features.append(self._feature_dict[feature](data))
                    
            event_features = np.concatenate(event_features, axis=1)
            features.append(event_features)
            
        features = np.concatenate(features)
        classes = np.concatenate(classes)
        
        return features, labels, classes
    
    def get_features(self):
        
        df = pd.DataFrame(self._values)
        df.columns = self._labels
        df.insert(0, 'class', self._classes)
        
        return df 

def IEMG(data):
    """Calculate integrated electromyogram """
    
    
    return np.sum(np.absolute(data), axis=1)
    

def window_function(n, mav_type=None):  
    w = np.ones(n)
    
    if mav_type == 1:
        w[:int(np.ceil(0.25 * n)) - 1] = 0.5
        w[int(np.floor((1-0.25) * n)):] = 0.5
        
    
    if mav_type == 2:
        r1 = np.arange(0, int(np.ceil(0.25 * n)) - 1)
        r2 = np.arange(int(np.floor((1-0.25) * n)), n)
        w[r1] = (1/0.25) * (r1 + 1) / n
        w[r2] = (1/0.25) * (n - (r2 + 1)) / n
        
    return w

def MAV(data):
    """Calculate mean absolute value

    Parameters
    ----------
    x : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    """
    
    return np.mean(np.absolute(data), axis=1)

def MMAV1(data):
    """Calculate modified MAV type 1"""
    
    for idx in range(data.shape[0]):
        data[idx, :, :] = (window_function(n=data.shape[1], mav_type=1) * data[idx,:,:].T).T
    
    return np.mean(np.absolute(data), axis=1)


def MMAV2(data):
    """Calculate modified MAV type 2"""
    for idx in range(data.shape[0]):
        data[idx, :, :] = (window_function(n=data.shape[1], mav_type=2) * data[idx,:,:].T).T
    
    
    return np.mean(np.absolute(data), axis=1)

    
    

def VAR(data):
    """Calculate variance"""
    
    return np.var(data, axis=1)
    

def SD(data):
    """Calculate standard deviation"""
    
    return np.std(data, axis=1)


def Kurt(data):
    """Calculate kurtosis
    

    Parameters
    ----------
    x : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    """
    
       
    return kurtosis(data, axis=1)
    
def Skew(data):
    """Calculate skewness
    

    Parameters
    ----------
    x : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    """
    
        
    return skew(data, axis=1)
    
def SSI(data):
    """Calculate Sample Square Integral
    

    Parameters
    ----------
    x : ndarray
        n_chan x n_times array of EMG data

    Returns
    -------
    Array of size n_chan

    """

    return np.sum(np.power(data, 2), axis=1)
    
def RMS(data):
    """Calculate Root Mean Square
    

    Parameters
    ----------
    x : ndarray
        n_chan x n_times array of EMG data

    Returns
    -------
    Array of size n_chan

    """
    
    
    return np.sqrt( (1/data.shape[1]) * np.sum(np.power(data, 2), axis=1))
    
def AAC(data):
    """Calculate Average Amplitude Change
    

    Parameters
    ----------
    x : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    """
    
       
    return np.mean(np.absolute(np.diff(data, axis=1)), axis=1)
        
    
def WL(data):
    """Calculate waveform length """


    return np.sum(np.absolute(np.diff(data, axis=1)), axis=1)



    