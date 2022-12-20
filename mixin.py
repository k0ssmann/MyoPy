#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import numpy as np

class TimeMixin:
    
    @property
    def times(self):
        return self._times
    
    def _set_times(self, times):
        self._times = times
        
    @property
    def tmin(self):
        return self.times[0]
    
    @property
    def tmax(self):
        return self.times[-1]
        
    
    
class EpochsMixin:

    @property
    def segments(self):
        return self._segments
    
    def _set_segments(self, segments):
        self._segments = segments
        
    @property
    def first_segment(self):
        return self.segments[0]
    
    @property
    def last_segment(self):
        return self.segments[-1]