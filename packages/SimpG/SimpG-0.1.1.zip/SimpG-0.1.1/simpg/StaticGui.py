from Igui import Igui
from enum import Enum
from pygame import Rect
import pygame
from math import trunc
from TreeNode import TreeNode


class SizeMethod(Enum):
    POINT_BASED = 0
    SIZE_BASED = 1

class StaticGui(Igui, Rect, TreeNode):

    def determine_coords(self):

        offset = self.border_size

        self.topl = (0, 0)
        self.topr = (self.width, 0)
        self.bottoml = (0, self.height)
        self.bottomr = (self.width, self.height)

        self.in_topl = (self.topl[0] + offset, self.topl[1] + offset)
        self.in_topr = (self.topr[0] - offset, self.topr[1] + offset)
        self.in_bottoml = (self.bottoml[0] + offset, self.bottoml[1] - offset)
        self.in_bottomr = (self.bottomr[0] - offset, self.bottomr[1] - offset)

        self.out_topl = (self.topl[0] - 1, self.topl[1] - 1)
        self.out_topr = (self.topr[0] + 1, self.topl[1] - 1)
        self.out_bottoml = (self.bottoml[0] - 1, self.bottoml[1] + 1)
        self.out_bottomr = (self.bottomr[0] + 1, self.bottomr[1] + 1)

    def draw_corners(self):
        if self.border_size > 1:
            # top-left corner
            pygame.draw.rect(self.SURFACE, self.border_color, ((0, 0), (self.border_size, self.border_size)), 0)
            # top-right corner
            pygame.draw.rect(self.SURFACE, self.border_color, ((self.width + 1, 0), (-self.border_size, self.border_size)), 0)
            # bottom-left corner
            pygame.draw.rect(self.SURFACE, self.border_color, ((0, self.height + 1), (self.border_size, -self.border_size)), 0)
            # bottom-right corner
            pygame.draw.rect(self.SURFACE, self.border_color, ((self.width + 1, self.height + 1), (-self.border_size, -self.border_size)), 0)

    def draw_border(self):
        border_dim = (self.width - trunc(self.border_size - 1), self.height - trunc(self.border_size - 1))
        border_start = (trunc((self.border_size - 1)/2), trunc((self.border_size - 1)/2))

        pygame.draw.rect(self.SURFACE, self.border_color, (border_start, border_dim), self.border_size)

    def set_border_size(self, size):
        self.border_size = size

    def set_border_color(self, color):
        self.border_color = color

    def __init__(self, render_dest, start_pos, end_pos_or_size, sizing_method = SizeMethod.POINT_BASED):
        self.border_color = (255, 255, 255)
        self.border_size = 0

        self.topleft = start_pos

        if sizing_method == SizeMethod.POINT_BASED:
            self.width = end_pos_or_size[0] - start_pos[0]
            self.height = end_pos_or_size[1] - start_pos[1]

        elif sizing_method == SizeMethod.SIZE_BASED:
            self.width = end_pos_or_size[0]
            self.height = end_pos_or_size[1]

        self.SURFACE = pygame.Surface((self.width, self.height))

        self.determine_coords()

        TreeNode.__init__(self, render_dest)

    def update_surface(self):
        self.determine_coords()
        self.draw_border()
        self.draw_corners()

    def set_transparency(self, alpha):
        self.SURFACE.set_alpha(alpha)

    def render(self, parent):
        return parent.SURFACE.blit(self.SURFACE, self)

