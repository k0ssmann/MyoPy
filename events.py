#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import numpy as np

def find_event_begin(events):
    """
    

    Parameters
    ----------
    x : ndarray
        An array of event id.

    Returns
    -------
    None.

    """
    
    events = np.insert(events, 0, -1)
    events = np.where(np.equal(events, np.roll(events, 1)), -1, events)
    return  events[1:]

def binary2integer(x, ttl_inversed):
    return x.dot(1 << np.arange(x.shape[-1])) if ttl_inversed else x.dot(1 << np.arange(x.shape[-1] - 1, -1, -1))


def find_events(raw):
    
    info = raw.info
    picks = [i for i, chan in enumerate(info['chs']) if chan['ch_type'] in ['TTL', 'event_id']]
    
    if 'ttl_inversed' in info['misc']:
        event_ids = binary2integer(raw._data[:, picks], info['misc']['ttl_inversed'])
        start_ids = find_event_begin(event_ids)
        mask = np.ma.masked_where(start_ids > -1, start_ids).mask
        times = raw.times[mask]
        event_ids = event_ids[mask]
        
        return np.array([times, event_ids], dtype=int).T
