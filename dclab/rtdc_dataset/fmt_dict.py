#!/usr/bin/python
# -*- coding: utf-8 -*-
"""RT-DC dictionary format"""
from __future__ import division, print_function, unicode_literals

import hashlib
import time

import numpy as np

from dclab import definitions as dfn
from .config import Configuration
from .core import RTDCBase


class RTDC_Dict(RTDCBase):
    def __init__(self, ddict):
        """Dictionary-based RT-DC data set 
        
        Parameters
        ----------
        ddict: dict
            Dictionary with keys from `dclab.definitions.uid` (e.g. "area", "defo")
            with which the class will be instantiated.
            The configuration is set to the default configuration of dclab.
        """
        assert ddict
        
        super(RTDC_Dict, self).__init__()

        t = time.localtime()
        
        # Get an identifying string
        keys = list(ddict.keys())
        keys.sort()
        ids = hashlib.md5(ddict[keys[0]]).hexdigest()
        self._ids = ids
        self.path = "none"
        self.title = "{}_{:02d}_{:02d}/{}.dict".format(t[0], t[1], t[2],ids)


        # Populate events
        self._events = {}
        for key in ddict:
            kk = dfn.cfgmaprev[key.lower()]
            self._events[kk] = ddict[key]

        # Populate empty columns
        fill0 = np.zeros(len(ddict[list(ddict.keys())[0]]))
        for key in dfn.rdv:
            if not key in self._events:
                self._events[key] = fill0

        # Set up filtering
        self.config = Configuration(rtdc_ds=self)
        self._init_filters()


    def __hash__(self):
        return hash(self._ids)