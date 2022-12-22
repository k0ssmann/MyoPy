#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Algorithms for EMG event detection

"""

#from ..epochs import Epochs
import numpy as np
from scipy import ndimage

def _moving_average(x, window_size=5):
    i = 0
    moving_averages = []
    while i < x.size - window_size + 1:
        window = x[i : i + window_size]
        # Calculate the average of current window
        window_average = np.mean(window)
        #v = 1/window_size * np.sum(np.power(window, 2)) - np.power(1/window_size * np.sum(window), 2)
          
        # Store the average of current
        # window in moving average list
        moving_averages.append(window_average)
          
        # Shift window to right by one position
        i += 1
    
    return np.array(moving_averages)
        

def CFAR(x, n_train, n_guard, rate_fa=0.05, window_size=5):
    """Constant false alarm rate with modified threshold and morphological hole filling
    
    Kang, K.; Rhee, K.; Shin, H.-C. Event Detection of Muscle Activation Using an Electromyogram. 
    Appl. Sci. 2020, 10, 5593. https://doi.org/10.3390/app10165593 
    
    Parameters
    ----------
    x : Instance of raw or epochs
        Instance of raw or epochs containing (non-)segmented data
    n_train : int
        Number of training cells
    n_guard : int
        Number of guard cells
    rate_fa : float, optional
        False alarm rate. The default is 0.05.
    window_size : int
        Window size for mean absolute value

    Returns
    -------
    onset : TYPE
        DESCRIPTION
    offset : TYPE
        DESCRIPTION

    """
    
    data = x.get_data()
    traces = []
    
    n_cells = data.shape[1]
    n_train_per_side = int(np.floor(n_train / 2))
    n_guard_per_side = int(np.floor(n_guard / 2))
    n_side = n_guard_per_side + n_train_per_side 
    
    alpha = n_train * (np.power(rate_fa, -1/n_train) - 1)
    
    
    for d in data:
        
        ch_trace = []
        
        for chan in range(d.shape[1]):
            
            moving_average = _moving_average(d[:, chan])
            binarized_signal = []
            
            for n in range(min(n_cells - n_side, moving_average.size)):
                
                lower_train = moving_average[n-n_side : n-n_guard_per_side]
                upper_train = moving_average[n+n_guard_per_side+1: n+n_side+1]
                training_cells = np.concatenate([lower_train, upper_train])
                
                cfar_threshold = alpha * np.median(training_cells)
                modified_threshold = min(cfar_threshold, np.std(data[:, chan]))
                
                if moving_average[n] >= modified_threshold:
                    binarized_signal.append(1)
                else:
                    binarized_signal.append(0)
                    
            eroded_signal = ndimage.binary_erosion(binarized_signal)
            dilated_signal = ndimage.binary_dilation(eroded_signal)
            
            ch_trace.append(dilated_signal)
            
        traces.append(ch_trace)
        
    times = []
    traces = np.array(traces)
    
    for trace in traces:
        
        for chan in range(trace.shape[0]):
            
            binary = trace[chan, :]
            if np.all(binary == True) or np.all(binary == False):
                continue
            
            onset_index = np.where(binary == True)[0][0]
            times.append(x.times[onset_index])
    

    return np.array(times)