#!/usr/bin/env python
# encoding: utf-8
"""
query.py

query phenomizer and store the results in a ordered dictionary.

Created by Måns Magnusson on 2015-02-02.
Copyright (c) 2015 __MoonsoInc__. All rights reserved.
"""
from __future__ import print_function

import logging
import sys
import os
import click
import requests

from pprint import pprint as pp

def parse_result(line):
    """
    Parse the result line of a phenomizer request.
    
    Arguments:
        line (str): A raw output line from phenomizer
    
    Returns:
         result (dict): A dictionary with the phenomizer info:
             {
                 'p_value': float,
                 'gene_id': str,
                 'omim_id': int,
                 'orphanet_id': int,
                 'decipher_id': int,
                 'any_id': int,
                 'mode_of_inheritance':str,
                 'description': str,
                 'raw_line': str
             }
             
    """
    result = {
        'p_value': None,
        'gene_id': None,
        'omim_id': None,
        'orphanet_id': None,
        'decipher_id': None,
        'mode_of_inheritance':None,
        'description': None,
        'raw_line': line
    }
    
    result_line = line.decode('UTF-8')
    result_line = result_line.rstrip().split('\t')
    
    try:
        result['p_value'] = float(result_line[0])
    except ValueError:
        pass
    
    try:
        medical_litterature = result_line[2].split(':')
        if medical_litterature[0] == 'OMIM':
            result['omim_id'] = int(medical_litterature[1])
            result['any_id'] = int(medical_litterature[1])
        elif medical_litterature[0] == 'DECIPHER':
            result['decipher_id'] = int(medical_litterature[1])
            result['any_id'] = int(medical_litterature[1])
        elif medical_litterature[0] == 'ORPHANET':
            result['orphanet_id'] = int(medical_litterature[1])
            result['any_id'] = int(medical_litterature[1])
    except IndexError:
        pass
    
    try:
        description = result_line[3]
        result['description'] = description
    except IndexError:
        pass
    
    try:
        gene_id = result_line[4]
        result['gene_id'] = gene_id
    except IndexError:
        pass
    
    return result

def query_phenomizer(usr, pwd, hpo_terms):
    """
    Query the phenomizer web tool
    
    Arguments:
        usr (str): A username for phenomizer
        pwd (str): A password for phenomizer
        hpo_terms (list): A list with hpo terms
    
    Returns:
        raw_answer : The raw result from phenomizer
    """
    basic_string = 'http://compbio.charite.de/phenomizer/phenomizer/PhenomizerServiceURI'
    questions = {'mobilequery':'true', 'terms':','.join(hpo_terms), 'username':usr, 'password':pwd}
    try:
        r = requests.get(basic_string, params=questions, timeout=10)
    except requests.exceptions.Timeout:
        raise RuntimeError("The request timed out.")
        
    if not r.status_code == requests.codes.ok:
        raise RuntimeError("Phenomizer returned a bad status code: %s" % r.status_code)
    
    r.encoding = 'utf-8'
    
    return r

def query(usr, pwd, hpo_terms):
    """
    Query the phenomizer web tool
    
    Arguments:
        usr (str): A username for phenomizer
        pwd (str): A password for phenomizer
        hpo_terms (list): A list with hpo terms
    
    Returns:
        parsed_terms (list): A list with the parsed HPO terms
     
    """
    
    raw_result = query_phenomizer(usr, pwd, hpo_terms)
    
    parsed_terms = (parse_result(line) for line in raw_result.iter_lines())
    # for line in raw_result.iter_lines():
    #     parsed_terms.append(parse_result(line))
    
    return(parsed_terms)

def validate_term(usr, pwd, hpo_terms):
    """
    Validate if the HPO term exists.
    
    Check if there are any result when querying phenomizer.
    
    Arguments:
        usr (str): A username for phenomizer
        pwd (str): A password for phenomizer
       hpo_term (string): Represents the hpo term
    
    Returns:
        result (boolean): True if term exists, False otherwise
    
    """
    
    result = True
    try:
        query_phenomizer(usr, pwd, [hpo_terms])
    except RuntimeError as err:
        result = False
    
    return result
    
