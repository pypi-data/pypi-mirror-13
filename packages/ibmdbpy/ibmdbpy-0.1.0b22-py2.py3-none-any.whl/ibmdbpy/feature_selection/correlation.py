#!/usr/bin/env python
# -*- coding: utf-8 -*-
#-----------------------------------------------------------------------------
# Copyright (c) 2015, IBM Corp.
# All rights reserved.
#
# Distributed under the terms of the BSD Simplified License.
#
# The full license is in the LICENSE file, distributed with this software.
#-----------------------------------------------------------------------------

#from numbers import Number
from collections import OrderedDict

#from ibmdbpy.feature_selection import entropy

import ibmdbpy
from ibmdbpy.internals import idadf_state
from ibmdbpy.utils import timed

import numpy as np
#from numpy import log2
import pandas as pd

import six

from ibmdbpy.feature_selection.private import _check_input

#import ibmdbpy

@idadf_state
@timed
def pearson(idadf, target, features = None):
    numerical_columns = idadf._get_numerical_columns()
    if target not in numerical_columns:
        raise TypeError("Correlation-based measure not available for non-numerical target %s"%target)
    
    target, features = _check_input(idadf, target, features)
    
    numerical_features = [x for x in features if x in numerical_columns]
    agg_list = ["CORRELATION(\"%s\",\"%s\")"%(x, target) for x in numerical_features]
    agg_string = ', '.join(agg_list)
    
    name = idadf.internal_state.current_state
    data = idadf.ida_query("SELECT %s FROM %s"%(agg_string, name), first_row_only = True)
    
    if len(features) > 1:
        value_dict = OrderedDict()
        i = 0
        for feature in features:
            if feature not in numerical_columns:
                value_dict[feature] = np.nan
            else:
                value_dict[feature] = data[i]
                i += 1  
        result = pd.Series(value_dict)
        result.index = features
        return result 
    else:
        if features[0] not in numerical_columns:
            return np.nan
        else:
            return data[0]
  
@idadf_state
@timed          
def spearman(idadf, target, features = None):
    numerical_columns = idadf._get_numerical_columns()
    if target not in numerical_columns:
        raise TypeError("Correlation-based measure not available for non-numerical target %s"%target)
    
    target, features = _check_input(idadf, target, features)
    
    numerical_features = [x for x in features if x in numerical_columns] + [target]
    agg_list = ["CAST(RANK() OVER (ORDER BY \"%s\") AS INTEGER) AS \"%s\""%(x, x) for x in numerical_features]
    
    non_numerical_columns = [column for column in idadf.columns if column not in numerical_columns]
    for column in non_numerical_columns:
        agg_list.append("\"" + column + "\"")
    agg_string = ', '.join(agg_list)
    
    expression = "SELECT %s FROM %s"%(agg_string, idadf.name)
    
    viewname = idadf._idadb._create_view_from_expression(expression)
    
    try:
        idadf_rank = ibmdbpy.IdaDataFrame(idadf._idadb, viewname)
        return pearson(idadf_rank, target = target)
    except:
        raise
    finally:
        idadf._idadb.drop_view(viewname)
    
    
    
 
        
        

        