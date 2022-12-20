#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import pickle
import json
from .io.base import BaseRaw

class Raw(BaseRaw):
    
    def __init__(self, fname, info=None):
        
        data, events, info = self._read_file(fname, info)
        super(Raw, self).__init__(info, data, events)
    
    
    def _read_file(self, fname, info):
        
        try:
            data = pd.read_pickle(fname)
        except pickle.UnpicklingError as e:
            raise e
            
        event_column = next((s for s in data.columns if 'event' in s))
        events = data[event_column].to_numpy(dtype=np.int64)
        data = np.transpose(data.loc[:, data.columns != event_column].to_numpy(dtype=np.float64))
        
        if isinstance(info, str):
            with open(info, 'r') as f:
                info = json.load(f)
        
        if info is not None:
            info['orig_ch'] = event_column
        
        return data, events, info


def read_raw(fname, info=None):
    """Read raw data
    

    Parameters
    ----------
    fname : str
        Path to file.
    info : dict | str, optional
        Dictionary containing information on sensor data or path to file containing it. The default is None.

    Returns
    -------
    Instance of Sensor

    """
    
    return Raw(fname, info)

