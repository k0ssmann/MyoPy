#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from copy import deepcopy

class Info(dict):
    """Measurement info"""
    
    
    _attributes = {
        'fnames': 'fnames cannot be set directly',
        'ch_names': 'ch_names cannot be set directly',
        'chs': 'chs cannot be set directly',
        'sfreq': 'sample rate cannot be set directly',
        'nchan': 'nchan cannot be set directly',
        'misc': 'misc cannot be set directly',
        'orig_ch': 'orig_ch cannot be set directly'
        }
    
    def __init__(self, *args, **kwargs):
        self._unlocked = True
        super().__init__(*args, **kwargs)
        self._unlocked = False
        
    def __setitem__(self, key, val):
        """Attribute setter."""
        unlocked = getattr(self, '_unlocked', True)
        if key in self._attributes:
            if not unlocked:
                raise RuntimeError(self._attributes[key])
        else:
            raise RuntimeError(f"Setting of key {repr(key)} is not supported")
        
        super().__setitem__(key, val)
    
    def __update__(self, **kwargs):
        """Update method using __setitem__()."""
        for key, val in kwargs.items():
            self[key] = val
            
    def __deepcopy__(self, memo):
        # Create a new instance of the class
        new_obj = self.__class__()
        new_obj._unlocked = True
        # Deep copy the dictionary attributes
        for key, value in self.items():
            new_obj[key] = deepcopy(value, memo)
        # Deep copy the attributes that are not part of the dictionary
        for attr in ['_attributes', '_unlocked']:
            value = getattr(self, attr)
            setattr(new_obj, attr, deepcopy(value, memo))
            
        new_obj.unlocked = False
        return new_obj
            
    def copy(self):
        """ Returns a deepcopy of the instance """
        return deepcopy(self)
    
def create_info(ch_names, sfreq, ch_type=None):
    """
    Create an instance of the Info class.
    
    Parameters
    ----------
    ch_names : int or list of str
        If an int, creates a list of str with values from 1 to the int.
        Otherwise, uses the provided list of str as is.
    sfreq : float
        The sample rate in Hz.
    ch_type : str, optional
        The type of channels. Default is None.
        
    Returns
    -------
    info : Info
        An instance of the Info class.
    """
    if isinstance(ch_names, int):
        if ch_type:
            ch_names = [f"{ch_type}{i}" for i in range(1, ch_names+1)]
        else:
            ch_names = [str(i) for i in range(1, ch_names+1)]
    return Info({
        'fnames': [],
        'ch_names': ch_names,
        'sfreq': sfreq,
        'chs': [{'ch_name': ch_name, 'ch_type': ch_type} for ch_name in ch_names],
        'nchan': len(ch_names),
        'misc': {}
    })


    