#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb  9 16:14:57 2021

@author: mike_ubuntu
"""

from dataclasses import dataclass

from epde.cache.cache import Cache
#from epde.supplementary import flatten

def init_caches(set_grids : bool = False):
    global tensor_cache, grid_cache
    tensor_cache = Cache()
    if set_grids:
        grid_cache = Cache()
    else:
        grid_cache = None
    
def set_time_axis(axis : int):
    global time_axis
    time_axis = axis
    
def init_eq_search_operator(operator):
    global eq_search_operator
    eq_search_operator = operator

def init_sys_search_operator(operator):
    global sys_search_operator
    sys_search_operator = operator
    
def delete_cache():
    global tensor_cache, grid_cache
    try:
        del tensor_cache
    except NameError:
        print('Failed to delete tensor cache due to its inexistance')
    try:
        del grid_cache
    except NameError:
        print('Failed to delete grid cache due to its inexistance')
        
@dataclass
class Verbose_Manager:
    plot_DE_solutions : bool
    iter_idx : bool
    iter_fitness : bool
    iter_stats : bool
    show_warnings : bool
    
def init_verbose(plot_DE_solutions : bool = False, show_iter_idx : bool = False, 
                 show_iter_fitness : bool = False, show_iter_stats : bool = False, 
                 show_warnings : bool = False):
    global verbose
    verbose = Verbose_Manager(plot_DE_solutions, show_iter_idx, show_iter_fitness, show_iter_stats)
    