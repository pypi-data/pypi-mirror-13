# -*- coding: utf-8 -*-
"""
Created on Mon Dec 14 11:31:52 2015

@author: efouche
"""

from collections import OrderedDict

import itertools 

from ibmdbpy.feature_selection.entropy import entropy 

from ibmdbpy.internals import idadf_state
from ibmdbpy.utils import timed

from numpy import log2
import numpy as np 
import pandas as pd

import six


from ibmdbpy.feature_selection.private import _compute_entropy, _fill_matrix
from ibmdbpy.feature_selection.private import _check_input, _check_input_for_matrix


@idadf_state
@timed
def chisquare(idadf, target = None, features = None):
    """
    chisquare as defined in 
    A Comparative Study on Feature Selection and Classification Methods Using 
    Gene Expression Profiles and Proteomic Patterns. (GIW02F006)
    """
    # Check input
    target, features = _check_input(idadf, target, features)
    chisquare_dict = dict()
    length = len(idadf)
    
    if target is not None:
        count = idadf.count_groupby(target)
        count_serie = count["count"]
        count_serie.index = count[target]
        C = dict(count_serie)
        
        for feature in features:
            count = idadf.count_groupby(feature)
            count_serie = count["count"]
            count_serie.index = count[feature]
            R = dict(count_serie)
            
            count = idadf.count_groupby([feature , target])
            
            chisquare = 0            
            for target_class in C.keys():
                count_target = count[count[target] == target_class][[feature, "count"]]
                A_target = count_target['count']
                A_target.index = count_target[feature]
                
                for feature_class in A_target.index:
                    a = A_target[feature_class]
                    e = R[feature_class] * C[target_class] / length
                    chisquare += ((a - e)**2)/e
            
            chisquare_dict[feature] = chisquare
                    
        # Output
        if len(features) > 1:
            result = pd.Series(chisquare_dict)
            result.sort(ascending = False) 
        else:
            result = chisquare_dict[feature[0]]
    else:
        raise NotImplementedError("TODO")
        
    return result