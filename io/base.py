#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
from copy import deepcopy
import pandas as pd
from ..mixin import TimeMixin 
from ..info import Info
from ..viz import RawPlot
import pickle

class BaseRaw(TimeMixin):
    """Base class for raw data
    
    Parameters
    ----------
    data : ndarray
        n_chan x n_times array of data
        
    first_samp : int
        Index of the first sample 
        
    last_samp : int
        Index of the last sample
    
    """
    def __init__(self, info, data, events=None, first_samp=0, last_samp=None, dtype=np.float64):

        if not isinstance(info, Info):
            raise RuntimeError('Argument info must be an instance of Info')
        
        if data.dtype != np.float64:
            raise RuntimeError('dtype of argument data must be float64, '
                               'but is %s' % data.dtype)
        
        self.info = info
        self._data = data
        
        assert isinstance(first_samp, int)
        
        if last_samp is None:
            last_samp = first_samp + self._data.shape[0] - 1
        
        self._last_samp = last_samp
        self._first_samp = first_samp
        
        self._data = self._data[:, self.first_samp:self.last_samp]
        
        assert len(self) == self.times.size, "this should not happen"
        
        
    @property
    def first_samp(self):
        """First sample"""
        return self._first_samp
    
    @property
    def last_samp(self):
        """Last sample"""
        return self._last_samp
    
    @property
    def first_time(self):
        """First time point in s"""
        return self.first_samp / float(self.info['sfreq']) 
    
    @property
    def last_time(self):
        """Last time point in ms"""
        return self.last_samp / float(self.info['sfreq']) 
    
    @property
    def times(self):
        """Time points in ms"""
        return np.arange(self.first_time, self.last_time + float(1/self.info['sfreq']), float(1/self.info['sfreq']))
    
    @property
    def n_times(self):
        """Number of time points"""
        return self.last_samp - self.first_samp + 1
    
    def __len__(self):
        """
        Return the number of time points.

        Returns
        -------
        n_times : int
            Number of time points.

        """
        return int(self.n_times)
    
    
    def to_data_frame(self):
        """ Convert to DataFrame """
        
        df = pd.DataFrame(data=self._data, columns=self.info['ch_names'])
        df['time'] = self.times
        
        return df
    
    def get_data(self):
        """
        

        Returns
        -------
        ndarray
            Array of size nchan x n_times containing data
        ndarray
            Array of size n_times containing time points

        """
        return self._data, self.times
    
    def copy(self):
        """ Returns a deepcopy of the instance """
        return deepcopy(self)
    
    def append(self, raw):
        """Append instances of Raw
        

        Parameters
        ----------
        raw : fne.Raw
            Instance of Raw to append


        """
        assert self.info['nchan'] == raw.info['nchan'], 'n_chan does not match'
        # TODO: adjust info['fnames']
        new_data = np.append(self._data, raw._data, axis=0)
        last_samp = self.first_samp + new_data.shape[0] - 1
        
        self._data = new_data
        self._last_samp = last_samp
        
    def plot(self, picks=None):
        
        return RawPlot(self.info, self._data, self.times, picks=picks)
        
def concatenate_raws(raws):
    """Concatenates a list of raws
    

    Parameters
    ----------
    raws : list
        A list of Sensor instances.

    Returns
    -------
    raw : Sensor
        A sensor instances with appended raw data.

    """
    
    raw = raws[0]
    
    for r in raws[1:]:
        raw.append(r)
    
    return raw
    
    