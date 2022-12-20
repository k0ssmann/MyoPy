#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from ..base import BaseRaw
import numpy as np
import pandas as pd 

class Tables(BaseRaw):
    def __init__(self, fname, info, col_data, col_events=None, ttl_inversed=True, 
                 na_to_zero=True, delimiter=','):
        """
        Initialize a Tables instance.
        
        Parameters
        ----------
        fname : str
            The file name.
        info : Info
            The measurement info.
        col_data : int
            The column containing the data.
        col_events : int
            The column containing the events. Default is None.
        ttl_inversed : bool
            Whether the TTL is inverted. Default is True.
        skiprows : int
            Rows to be skipped. Default is 1 and corresponds to table header.
        delimiter : str
            The delimiter used in the file.
        converters : func
            Function to handle edge cases in table. Default is empty_convert().
        """
        

        usecols = [col_data]
        if col_events:
           usecols.append(col_events)
           
        usecols = [item for sublist in usecols for item in sublist]
        
        if len(col_data) > len(info['chs']):
            raise RuntimeError('Number of channels in Info larger than selected data columns.')
        
        
        info._unlocked = True
        
        info['fnames'].append(fname)

        if col_events:
            if len(col_events) > 1:
                info['misc']['ttl_inversed'] = ttl_inversed
                ch_type = 'TTL'
                for i, ch in enumerate(col_events):
                    ch_name = f"TTL{i+1}"
                    if ch_name not in info['ch_names']:
                        info['chs'].append({'ch_name': ch_name, 'ch_type': ch_type})
                        info['ch_names'].append(ch_name)
            else:
                ch_type = 'event_id'
                if ch_type not in info['ch_names']:
                    info['chs'].append({'ch_name': ch_type, 'ch_type': ch_type})
                    info['ch_names'].append(ch_name)
        info.update({'nchan': len(info['ch_names'])})
        
        # Handle duplicates in chs
        chs = info['chs']
        unique_chs = list({v['ch_name']:v for v in chs}.values())
        info['chs'] = unique_chs
            
        info._unlocked = False
        
        data = pd.read_csv(fname, delimiter=delimiter, usecols=usecols)
        
        if na_to_zero:
            data.fillna(0)
        
        for col in data.columns:
          # Replace commas with points in each column because some shitters use 
          # comma-seperated floats
          data[col] = data[col].apply(lambda x: pd.to_numeric(str(x).replace(',', '.')))
        
        data = data.to_numpy()
        
        super(Tables, self).__init__(info, data)
            

def read_table(fname, info, col_data, col_events=None, ttl_inversed=True, 
               na_to_zero=True, delimiter=','):
    
    """
    Parameters
    ----------
    fname : str
        Path to table containing EMG/FMG data
    info : dict
        Dictionary containing information on measurements
    col_data : int | list
        Integer or list of integers of column ids to use for data
    col_events : int | list, optional
        Integer or list of column ids to use for events. 
        If col_events > 1, columns are interpreted as TTL bits. The default is None.
    ttl_inversed : boolean, optional
        If true, inversion of TTL bits is taken into account during conversion. The default is None.
    skiprows : int | list, optional
        Integer or list of integers ofrow idsto skip. The default is 1, corresponds
        to table header.

    Returns
    -------
    raw : instance of Tables
        A Raw object containing data from tables.

    """
    
    return Tables(fname=fname, info=info, col_data=col_data, 
                  col_events=col_events, ttl_inversed=ttl_inversed, 
                  na_to_zero=na_to_zero, delimiter=delimiter)
    
   
    