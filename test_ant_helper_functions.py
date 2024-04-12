# -*- coding: utf-8 -*-
"""
Created on Tue Aug  2 17:16:37 2022

@author: VERA7
tests someof the ant_helper_functions
"""

from ant import ant_helper_functions as ant_funcs

def test_find_id():
    """check if right id found in records"""
    test_records = [
                {'id': 'b228477c-c82b-459f-af89-407ff71f9a72',
                 'Naam': 'Westerschelde',
                 'Methode': 'IPM'},
                {'id': 'fc04022d-896b-41a5-b305-e70c8a1cd547',
                 'Naam': 'Waddenzee',
                 'Methode': 'Database'},
                {'id': '10958d59-f3dd-45f8-98c8-cce9c4a3dd2a',
                 'Naam': 'Hollandse IJssel',
                 'Methode': 'Database'},
                {'id': 'df2985bd-7aa4-4bf6-b745-a50054e7e5ce',
                'Naam': 'Waddenzee',
                'Methode': 'IPM'},
                {'id': '5d4bb442-1934-4258-b6cd-8eb226a8c627',
                 'Naam': 'Oosterschelde',
                 'Methode': 'Database'}]
    
    expected_id = 'df2985bd-7aa4-4bf6-b745-a50054e7e5ce'
    
    found_id = ant_funcs.find_id(test_records, cols_to_search = ['Naam', 'Methode'],
                                 items_to_find  = ['Waddenzee', 'IPM'])
    
    assert expected_id == found_id, "did not find the right record id"