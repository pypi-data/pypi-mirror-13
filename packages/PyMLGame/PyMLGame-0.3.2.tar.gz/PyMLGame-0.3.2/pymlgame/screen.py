# -*- coding: utf-8 -*-

"""
PyMLGame - Screen
"""

import socket

from pymlgame.locals import BLACK
from pymlgame.surface import Surface


class Screen(object):
    """
    Represents the Mate Light screen and has all the drawing methods.
    """
    def __init__(self, host='127.0.0.1', port=1337, width=40, height=16):
        """
        Create a screen with default size and fill it with black pixels.
        """
        self.host = host
        self.port = port
        self.width = width
        self.height = height

        self.matrix = None
        self.reset()

    def reset(self):
        """
        Fill the screen with black pixels
        """
        surface = Surface(self.width, self.height)
        surface.fill(BLACK)
        self.matrix = surface.matrix

    def update(self):
        """
        Sends the current screen contents to Mate Light
        """
        display_data = []
        for y in range(self.height):
            for x in range(self.width):
                for color in self.matrix[x][y]:
                    display_data.append(int(color))

        checksum = bytearray([0, 0, 0, 0])
        data_as_bytes = bytearray(display_data)
        data = data_as_bytes + checksum
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(data, (self.host, self.port))

    def blit(self, surface, pos=(0, 0)):
        """
        Blits a surface on the screen at pos

        :param surface: Surface to blit
        :param pos: Top left corner to start blitting
        :type surface: Surface
        :type pos: tuple
        """
        for x in range(surface.width):
            for y in range(surface.height):
                point = (x + pos[0], y + pos[1])
                if self.point_on_screen(point):
                    self.matrix[point[0]][point[1]] = surface.matrix[x][y]

    def point_on_screen(self, pos):
        """
        Is the point still on the screen?

        :param pos: Point
        :type pos: tuple
        :return: Is it?
        :rtype: bool
        """
        if 0 <= pos[0] < self.width and 0 <= pos[1] < self.height:
            return True
        else:
            return False
