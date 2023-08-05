# -*- coding: utf-8 -*-

"""
PyMLGame - Event
"""

from pymlgame.locals import E_KEYDOWN, E_KEYUP


class Event(object):
    def __init__(self, uid, type, data=None):
        self.uid = uid
        self.type = type
        if type == E_KEYDOWN or type == E_KEYUP:
            self.button = data
        else:
            self.data = data
