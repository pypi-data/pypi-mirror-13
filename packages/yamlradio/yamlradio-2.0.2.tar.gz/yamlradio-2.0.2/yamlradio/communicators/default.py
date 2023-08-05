#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# PYTHON_ARGCOMPLETE_OK

## Dependencies:    mplayer, argparse, argcomplete, pyYAML
## Author:          Gijs Timmers: https://github.com/GijsTimmers

## Licence:         CC-BY-SA-4.0
##                  http://creativecommons.org/licenses/by-sa/4.0/

## This work is licensed under the Creative Commons
## Attribution-ShareAlike 4.0 International License. To  view a copy of
## this license, visit http://creativecommons.org/licenses/by-sa/4.0/ or
## send a letter to Creative Commons, PO Box 1866, Mountain View,
## CA 94042, USA.

import sys

class Communicator(object):
    def __init__(self):
        self.oudeInfo = ""
        self.BREEDTE_TERMINAL = 80

    def processChannelName(self, zender):
        print("Speelt nu af: [{zender}]".format(zender=zender))
        
        ## Huidige radiozender weergeven als terminaltitel.
        sys.stdout.write("\x1b]2;{zender}\x07".format(zender=zender))
    
    def checkIfIcyIsNew(self, regel):
        ## Het oudeInfo/nieuweInfo-mechanisme
        ## is een mechanisme om iedere keer alleen het nieuwste ICY-bericht
        ## in het leesvenster te plaatsen.
        self.nieuweInfo = regel
        if self.nieuweInfo == self.oudeInfo:
            return None
        else:
            self.oudeInfo = self.nieuweInfo
            return self.nieuweInfo
            
    def processIcy(self, regel):
        ## Ontvangen ICY-tekst doorgeven aan checkIfIcyIsNew() om te kijken of
        ## ze nieuw is. Indien ze hetzelfde is, gebeurt er niks.
        
        regel = self.checkIfIcyIsNew(regel)
        if regel:  
            sys.stdout.write("\r" + " " * self.BREEDTE_TERMINAL)
            sys.stdout.write("\r" + "Info:         [{info}]".format(info=regel))
        else:
            sys.stdout.write("\r" + " " * self.BREEDTE_TERMINAL)
            sys.stdout.write("\r" + "Info:         [Geen informatie beschikbaar]".format(info=regel))
    
    def processVolumeUp(self):
        sys.stdout.write("\r" + " " * self.BREEDTE_TERMINAL)
        sys.stdout.write("\r" + "Info:         [{info}]".format(info="Volume ↑"))
    
    def processVolumeDown(self):
        sys.stdout.write("\r" + " " * self.BREEDTE_TERMINAL)
        sys.stdout.write("\r" + "Info:         [{info}]".format(info="Volume ↓"))