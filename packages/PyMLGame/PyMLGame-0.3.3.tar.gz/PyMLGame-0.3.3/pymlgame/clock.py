# -*- coding: utf-8 -*-

"""
PyMLGame - Clock
"""

import time


class Clock(object):
    """
    Measure the time to adjust drawing rates.
    """
    def __init__(self, fps):
        """
        Get a fresh Clock which ticks n times per second.

        :param fps: Target frames per second
        :type fps: int
        """
        self.fps = fps

    def tick(self):
        """
        Let the Clock tick.
        """
        #TODO: I think this is not the correct way. I should think about this again..
        time.sleep(1.0 / self.fps)
