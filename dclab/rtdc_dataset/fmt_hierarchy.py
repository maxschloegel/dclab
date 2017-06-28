#!/usr/bin/python
# -*- coding: utf-8 -*-
"""RT-DC hierarchy format"""
from __future__ import division, print_function, unicode_literals

import numpy as np

from .config import Configuration
from .core import RTDCBase
from .util import hashobj


class RTDC_Hierarchy(RTDCBase):
    def __init__(self, hparent):
        """A hierarchy child of a subclass of RTDCBase
        
        A few words on hierarchies:
        The idea is that a subclass of RTDCBase can use the filtered data of another
        subclass of RTDCBase and interpret these data as unfiltered events. This comes
        in handy e.g. when the percentage of different subpopulations need to
        be distinguished without the noise in the original data.
        
        Children in hierarchies always update their data according to the
        filtered event data from their parent when `apply_filter` is called.
        This makes it easier to save and load hierarchy children with e.g.
        ShapeOut and it makes the handling of hierarchies more intuitive
        (when the parent changes, the child changes as well).
        
        Parameters
        ----------
        hparent : instance of RTDCBase
            The hierarchy parent.
            
        Attributes
        ----------
        hparent : instance of RTDCBase
            Only hierarchy children have this attribute
        """
        super(RTDC_Hierarchy, self).__init__()
        self._events = {}

        self.path = hparent.path
        self.title = hparent.title + "_child"

        self.hparent = hparent

        ## Copy configuration
        cfg = hparent.config.copy()

        # Remove previously applied filters
        pops = []
        for key in cfg["filtering"]:
            if (key.endswith("min") or
                key.endswith("max") or
                key == "polygon filters"):
                pops.append(key)

        [ cfg["filtering"].pop(key) for key in pops ]
        # Add parent information in dictionary
        cfg["filtering"]["hierarchy parent"] = hparent.identifier

        self.config = Configuration(cfg = cfg)

        # Apply the filter
        # This will also populate all event attributes
        self.apply_filter()


    def __contains__(self, key):
        ct = False 
        if self.hparent.__contains__(key):
            value = self.hparent[key]
            if isinstance(value, np.ndarray):
                ct = True
        return ct


    def __getitem__(self, key):
        if key in self._events:
            return self._events[key]
        else:
            item = self.hparent[key]
            if isinstance(item, np.ndarray):
                return item[self.hparent._filter]
            else:
                msg = "Hierarchy does not implement {}".format(key)
                raise NotImplementedError(msg)


    def __len__(self):
        self.hparent.apply_filter()
        return np.sum(self.hparent._filter)


    def apply_filter(self, *args, **kwargs):
        """Overridden `apply_filter` to perform tasks for hierarchy child"""
        # Copy event data from hierarchy parent
        self.hparent.apply_filter()

        # update event index
        length = np.sum(self.hparent._filter)
        self._events["index"] = np.arange(1, length+1)

        self._init_filters()
        self._old_filters = {}

        if (hasattr(self, "_filter_manual") 
            and np.sum(1-self._filter_manual) != 0):
            msg = "filter_manual not supported in hierarchy!"
            raise NotImplementedError(msg)

        super(RTDC_Hierarchy, self).apply_filter(*args, **kwargs)


    @property
    def hash(self):
        """Hashes of hierarchy parents change if the parent changes"""
        hph = self.hparent.hash
        hfilth = hashobj(self.hparent._filter)
        return hashobj(hph+hfilth)
