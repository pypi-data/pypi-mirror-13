import pygame
from math import trunc

# This will be the base class for Complex interfaces. It will supply all features that every GUI requires to function properly
class Igui(pygame.Rect):

    def __init__(self):
        pass

    def update_surface(self):
        # Update the Surface of the GUI before rendering anything
        pass

    def render(self):
        # Instructions for how the GUI should be rendered.
        pass




