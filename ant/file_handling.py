# -*- coding: utf-8 -*-
"""
Created on Thu Jul 28 08:42:04 2022

@author: VERA7
contains functionality to get fingerprint
"""
from hashlib import md5

BLOCK_SIZE = 65536

def get_fingerprint_from_file(file_path):
    hash_method = md5()
    with open(file_path, 'rb') as input_file:
        buf = input_file.read(BLOCK_SIZE)
        while len(buf) > 0:
            hash_method.update(buf)
            buf = input_file.read(BLOCK_SIZE)

    return hash_method.hexdigest()
