#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pickle

def to_pickle(instance, filepath):
    with open(filepath, 'wb') as f:
        pickle.dump(instance, f)
    
def from_pickle(filepath):
    with open(filepath, 'rb') as f:
        return pickle.load(f)

