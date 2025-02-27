#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 13 14:45:14 2021

@author: mike_ubuntu
"""

import numpy as np
import epde.interface.interface as epde_alg

from epde.interface.prepared_tokens import Custom_tokens, Trigonometric_tokens, Cache_stored_tokens
from epde.evaluators import Custom_Evaluator

if __name__ == '__main__':

    t = np.linspace(0, 4*np.pi, 1000)
    u = np.load('/media/mike_ubuntu/DATA/EPDE_publication/tests/system/Test_data/fill366.npy') # loading data with the solution of ODE
    # Trying to create population for mulit-objective optimization with only 
    # derivatives as allowed tokens. Spoiler: only one equation structure will be 
    # discovered, thus MOO algorithm will not be launched.
    
    dimensionality = t.ndim - 1
    
    epde_search_obj = epde_alg.epde_search()

    '''
    --------------------------------------------------------------------------------------------------------------------------------
    Так как в этом примере мы будем использовать собственноручно-заданные семейства токенов, то для начала нужно ввести 
    функцию для получения значений токенов на сетке, определяющей область, для которой ищется дифф. уравнение, при фиксированных
    прочих параметрах. 
    
    В случае, если семейство "порождено" одним токеном (как, например, функции, обратные значениям сетки вида 1/x^n), то 
    можно задать одиночную лямба-, или обычную функцию. В случае, когда в семействе предполагается несколько функций, нужно 
    использовать словарь с ключами - названиями функций, значениями - соответсвующими лямбда-, или обычными функциями.
    
    Формат задания функции для оценки: не должно быть обозначенных аргументов, *args, и **kwargs. В kwargs будут передаваться все 
    параметры функций, а в *args - значения аргументов (координаты на сетке).
    '''
    custom_trigonometric_eval_fun =  {'cos' : lambda *grids, **kwargs: np.cos(kwargs['freq'] * grids[int(kwargs['dim'])]) ** kwargs['power'], 
                   'sin' : lambda *grids, **kwargs: np.sin(kwargs['freq'] * grids[int(kwargs['dim'])]) ** kwargs['power']}
    
    '''
    --------------------------------------------------------------------------------------------------------------------------------
    Задаём объект для оценки значений токенов в эволюционном алгоритме. Аргументы - заданная выше функция/функции оценки значений 
    токенов и лист с названиями параметров. 
    '''
    custom_trig_evaluator = Custom_Evaluator(custom_trigonometric_eval_fun, eval_fun_params_labels = ['freq', 'dim', 'power'])
    
    '''
    --------------------------------------------------------------------------------------------------------------------------------
    Задам через python-словарь диапазоны, в рамках которых могут браться параметры функций оценки токенов.
    
    Ключи должны быть в формате str и соотноситься с аргументами лямда-функций для оценки значения токенов. Так, для введённой
    выше функции для оценки значений тригонометрических функций, необходимы значения частоты, степени функции и измерения сетки, по 
    которому берётся аргумент с ключами соответственно 'freq', 'power' и 'dim'. Значения, соответствующие этим ключам, должны быть
    границы, в пределах которых будут искаться значения параметров функции при оптимизации, заданные в формате python-tuple из 
    2-ух элементов: левой и правой границы.

    Целочисленное значение границ соответствует дискретным значеням (например, при 'power' : (1, 3), 
    будут браться степени со значениями 1, 2 и 3); при действительных значениях (типа float) значения параметров 
    берутся из равномерного распределения с границами из значения словаря. Так, например, при значении 'freq' : (1., 3.), 
    значения будут выбираться из np.random.uniform(low = 1., high = 3.), например, 2.7183... 
    '''
    trig_params_ranges = {'power' : (1, 1), 'freq' : (0.95, 1.05), 'dim' : (0, dimensionality)} 
    
    '''
    --------------------------------------------------------------------------------------------------------------------------------
    Далее необходимо определить различия в значениях параметров, в пределах которых функции считаются идентичными, чтобы строить 
    уникальные структуры уравнений и слагаемых в них. Например, для эволюционного алгоритма можно считать, что различия между 
    sin(3.135 * x) и sin(3.145 * x) незначительны и их можно считать равными. 
    
    Задание значений выполняется следующим образом: ключ словаря - название параметра, значение - максимальный интервал, при котором токены
    счиатются идентичными.
    
    По умолчанию, для дискретных параметров равенство выполняется только при полном соответствии, а для действительно-значных аргументов
    равенство выполняется при разнице меньше, чем 0.05 * (max_param_value - min_param_value).
    '''
    trig_params_equal_ranges = {'freq' : 0.05}

    custom_trig_tokens = Custom_tokens(token_type = 'trigonometric', # Выбираем название для семейства токенов.
                                       token_labels = ['sin', 'cos'], # Задаём названия токенов семейства в формате python-list'a.
                                                                      # Названия должны соответствовать тем, что были заданы в словаре с лямбда-ф-циями.
                                       evaluator = custom_trig_evaluator, # Используем заранее заданный инициализированный объект для функции оценки токенов.
                                       params_ranges = trig_params_ranges, # Используем заявленные диапазоны параметров
                                       params_equality_ranges = trig_params_equal_ranges) # Используем заявленные диапазоны "равенства" параметров

    '''
    Расширим допустимый пулл токенов, добавив функции, обратные значениям координат (вида 1/x, 1/t, и т.д.). Для получения их
    значений зададим единую лямбда-функцию `custom_inverse_eval_fun`, и далее соответствующее семейство токенов.
    
    '''
    custom_inverse_eval_fun = lambda *grids, **kwargs: np.power(grids[int(kwargs['dim'])], - kwargs['power']) 
    custom_inv_fun_evaluator = Custom_Evaluator(custom_inverse_eval_fun, eval_fun_params_labels = ['dim', 'power'], use_factors_grids = True)    

    inv_fun_params_ranges = {'power' : (1, 2), 'dim' : (0, dimensionality)}
    
    custom_inv_fun_tokens = Custom_tokens(token_type = 'inverse', # Выбираем название для семейства токенов - обратных функций.
                                       token_labels = ['1/x_{dim}',], # Задаём названия токенов семейства в формате python-list'a.
                                                                     # Т.к. у нас всего один токен такого типа, задаём лист из 1 элемента
                                       evaluator = custom_inv_fun_evaluator, # Используем заранее заданный инициализированный объект для функции оценки токенов.
                                       params_ranges = inv_fun_params_ranges, # Используем заявленные диапазоны параметров
                                       params_equality_ranges = None) # Используем None, т.к. значения по умолчанию 
                                                                      # (равенство при лишь полном совпадении дискретных параметров)
                                                                      # нас устраивает.

    boundary = 10
    custom_grid_tokens = Cache_stored_tokens(token_type = 'grid', 
                                       boundary = boundary,
                                       token_labels = ['t'], 
                                       token_tensors={'t' : t},
                                       params_ranges = {'power' : (1, 1)},
                                       params_equality_ranges = None)
    
    epde_search_obj.fit(data = u, boundary=boundary, equation_factors_max_number = 2, coordinate_tensors = [t,], 
                        additional_tokens = [custom_trig_tokens, custom_inv_fun_tokens, custom_grid_tokens], field_smooth = False, memory_for_cache=5, data_fun_pow = 2)
    
    epde_search_obj.equation_search_results(only_print = True, level_num = 1) # showing the Pareto-optimal set of discovered equations 