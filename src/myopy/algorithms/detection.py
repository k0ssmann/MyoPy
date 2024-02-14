#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import numpy as np
from scipy import ndimage

def kang_onset_detection(signal, n_train, n_guard, rate_fa=0.05, threshold=None, 
                         window=5):
    """Determine onsets of EMG pulses using a cell-averaging CFAR algorithm
    with an adaptive threshold and morphological hole filling.


    Parameters
    ----------
    signal : list
        Input EMG signal
    n_train : int
        Number of training cells.
    n_guard : int
        Number of guard cells.
    rate_fa : float, optional
        False alarm rate. The default is 0.05.
    window_size : int, optional
        Window size for moving average. The default is 5.

    Returns
    -------
    onsets : ndarray
        Indices of EMG pulse onsets
        
    References
    -------
    Kang, K., Rhee, K., & Shin, H.-C. (2020). Event Detection of Muscle 
    Activation Using an Electromyogram. Applied Sciences, 10(16), 5593. 
    https://doi.org/10.3390/app10165593


    """
    
    n_cells = signal.size
    n_train_per_side = int(np.floor(n_train / 2))
    n_guard_per_side = int(np.floor(n_guard / 2))
    n_side = n_guard_per_side + n_train_per_side 
                
    # moving average
    mvgav = np.convolve(signal, np.ones((window,))/window, mode='valid')
    
    # calculate alpha
    alpha = n_train * (np.power(rate_fa, -1/n_train) - 1)

    
    # find onsets
    binarized_signals = []
    for n in range(min(n_cells - n_side, mvgav.size)):
        
        lower_train = mvgav[n-n_side : n-n_guard_per_side]
        upper_train = mvgav[n+n_guard_per_side+1: n+n_side+1]
        training_cells = np.concatenate([lower_train, upper_train])
        
        # calculate cfar threshold and modified threshold
        cfar_threshold = alpha * np.median(training_cells)
        adaptive_threshold = min(cfar_threshold, threshold * np.std(signal))
        
        if mvgav[n] >= adaptive_threshold:
            binarized_signals.append(1)
        else:
            binarized_signals.append(0)
    
    eroded_signals = ndimage.binary_erosion(binarized_signals)
    dilated_signals = ndimage.binary_dilation(eroded_signals)
    
    onsets = np.nonzero(np.where(np.equal(dilated_signals, np.roll(dilated_signals, 1)), 
                        False, dilated_signals))[0]
    
    return onsets, dilated_signals
    
