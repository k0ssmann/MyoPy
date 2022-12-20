#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
from copy import deepcopy
import pandas as pd
# import pyqtgraph as pg
# from pyqtgraph.Qt import QtCore
from .mixin import TimeMixin, EpochsMixin
from .io.base import BaseRaw
from .viz import EpochsPlot

class BaseEpochs(TimeMixin, EpochsMixin):
    
    def __init__(self, info, data, events, event_id=None, raw=None, picks=None, tmin=0, tmax=5.0):
        """
        

        Parameters
        ----------
        info : fne.Info
            Instance of fne.Info
        data : ndarray
            ndarray of n_epochs x n_samples x n_chan. If None, an instance of raw will be used.
        events : ndarray
            ndarray of n_events x 2 containing event onset and event_id
        event_id : list, optional
            A list of event IDs to be used. If None, all unique event IDs from events will be used.
        picks : list | slice, optional
            List of integers or slices corresponding to the channels to be used. The default is None.
        tmin : int, optional
            Start time of the epoch in ms relative to the time-locked event. The default is 0.
        tmax : int, optional
            End time of the epoch in ms relative to the time-locked event. The default is 500.

        """
        
        self.info = info
        self.picks = picks
        self._tmin = tmin
        self._tmax = tmax
        
        if event_id is None:
            self.event_id = np.unique(events[:,1])
        else:
            self.event_id = event_id
        
        self.events = events[np.isin(events[:,1], self.event_id),:]
        
        if self.events.size == 0:
           raise RuntimeError("No events were found.")
        
        times = np.arange(tmin, tmax + float(1/self.info['sfreq']), float(1/self.info['sfreq']))
        self._set_times(times)
        self._last_samp = int((np.absolute(tmax) + np.absolute(tmin)) * self.info['sfreq']) + 1
        
        if tmin > tmax:
            raise RuntimeError('tmin must be smaller than tmax.')
        
        
        if data is None:
            self._data = None
            self._raw_times = raw.times
            self._raw = raw
            self._epochs_from_raw()
        else:
            # TODO: Handle edge cases
            self._data = data
        
    @property
    def tmin(self):
        return self._tmin
    
    @property
    def tmax(self):
        return self._tmax
    
    def _epochs_from_raw(self):
        self._data = np.zeros((self.events.shape[0], self._last_samp, len(self.picks)))
                
        start_time = self.events[:, 0] + self.tmin
        end_time = self.events[:,0] + self.tmax 
        
        start_time[start_time < np.min(self._raw_times)] = np.min(self._raw_times)
        end_time[end_time > np.max(self._raw_times)] = np.max(self._raw_times)
        
        start_index = np.searchsorted( self._raw_times, start_time)
        end_index = np.searchsorted(self._raw_times, end_time)
        
        for i, sl in enumerate(list(zip(start_index, end_index + 1))):
            self._data[i,:,:] = self._raw._data[slice(*sl), self.picks]
        
    def get_data(self):
        """ Get data
        

        Returns
        -------
        ndarray
            ndarray of n_events x n_samples x n_chans of segmented data

        """
        return self._data
    
    def to_data_frame(self):
        """ Epochs to data frame
        

        Returns
        -------
        None.

        """
        
        ch_names = np.array(self.info['ch_names'])
        data = np.reshape(self._data, (self.events.shape[0]*self._last_samp, len(self.picks)))
        df = pd.DataFrame(data=data, columns=ch_names[self.picks])
        df['time'] = np.tile(self.times, (1, self.events.shape[0])).flatten()
        df['event_id'] = np.repeat(self.events[:, 1], self._last_samp)
        
        return df
    
    def copy(self):
        """Return copy of Epochs instance
        

        Returns
        -------
        inst : instance of Raw
            A copy of the instance

        """
        
        return deepcopy(self)
    
    def plot(self):
        return EpochsPlot(info=self.info, data=self._data, events=self.events, 
                          tmin=self.tmin, tmax=self.tmax, event_id=self.event_id, 
                          picks=self.picks)

    
    
class Epochs(BaseEpochs):
    
    def __init__(self, raw, events, event_id=None, picks=None, tmin=0, tmax=5.0):
        
        if not isinstance(raw, BaseRaw):
            raise RuntimeError("Argument raw must be an instance of fne.io.BaseRaw")
        
        info = deepcopy(raw.info)
        
        super(Epochs, self).__init__(info=info, data=None, events=events, 
                                     event_id=event_id, raw=raw, picks=picks, 
                                     tmin=tmin, tmax=tmax)
        
