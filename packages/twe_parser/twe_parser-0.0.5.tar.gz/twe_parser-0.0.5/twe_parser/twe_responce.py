#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
class TWE_Responce(object):
    r='^:(..)(..)(..)(..)(..)(........)(..)(....)(..)(....)(..)(..)(..)(..)(..)(..)(..)(..)(..)'
    group = {}
    enable = False
    
    def __init__( self, string ):
        self.string = string
        values = self.parse()

        if not values:
            return None

        self._setvalues( values )


    def parse( self, string=None ):
        if not string:
            string = self.string

        if type( string ) == bytes:
            string = string.decode()

        r = re.match( self.r, string )
        if r:
            g = r.groups()
            pr = {}
            pr['SID'], pr['COMMAND'], pr['PACKET'], pr['PROTOCOL'], pr['LQI'], pr['SNumber'], pr['DID'], pr['TIMESTAMP'], pr['RELATED'], pr['VOLTAGE'], pr['NONE'], pr['DIN'], pr['DICANGE'], pr['AD1'], pr['AD2'], pr['AD3'], pr['AD4'], pr['ADCOMP'], pr['SUM'] = g[0], bin(int(g[1],16)), g[2], int(g[3],16), hex(int(g[4],16)), hex(int(g[5],16)), hex(int(g[6],16)), int(g[7],16), g[8], int(g[9],16), g[10], bin(int(g[11],16)), bin(int(g[12],16)), int(g[13],16), int(g[14],16), int(g[15],16), int(g[16],16), bin(int(g[17],16)), hex(int(g[18],16))
            return pr
        else:
            return None

    def _setvalues( self, pr ):
        self.enable = True
        self.SID = pr['SID']
        self.COMMAND = pr['COMMAND']
        self.PACKET = pr['PACKET']
        self.PROTOCOL = pr['PROTOCOL']
        self.LQI = pr['LQI']
        self.SNumber = pr['SNumber']
        self.DID = pr['DID']
        self.TIMESTAMP = pr['TIMESTAMP']
        self.RELATED = pr['RELATED']
        self.VOLTAGE = pr['VOLTAGE']
        self.NONE = pr['NONE']
        self.DIN = pr['DIN']
        self.DICANGE = pr['DICANGE']
        self.AD1 = pr['AD1']
        self.AD2 = pr['AD2']
        self.AD3 = pr['AD3']
        self.AD4 = pr['AD4']
        self.ADCOMP = pr['ADCOMP']
        self.SUM = pr['SUM']
        self.group = pr

    def rsrp( self ):
        return ( 7 * int(self.LQI, 16) - 1970 ) / 20
