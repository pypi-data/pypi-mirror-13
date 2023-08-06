#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
にとりかわいい - Nitori is Pritty -
'''


__version__ = '0.0.1'
__author__  = 'Asahi Himura <himura@nitolab.com>'
__date__    = '13/2/2016'
__license__ = "BSD-3-Clause"


from .twe_responce import TWE_Responce

def parse( string ):
	return TWE_Responce( string )
