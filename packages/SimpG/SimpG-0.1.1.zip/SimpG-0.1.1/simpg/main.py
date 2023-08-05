import pygame
import os
import pygame.freetype
pygame.init()
from Window import Window
from StaticGui import StaticGui
from StaticGui import SizeMethod

def ButtonClicked(gui):
    gui.set_border_size(gui.border_size + 1)

def main():
    wind = Window((500, 500))

    gui = StaticGui(wind, wind.topleft, (100, 100), SizeMethod.SIZE_BASED)
    gui.set_border_color((255, 255, 255))

    gui2 = StaticGui(gui, gui.in_topl, (75, 75), SizeMethod.SIZE_BASED)
    gui2.set_border_color((255, 0, 0))

    gui3 = StaticGui(gui2, gui2.in_topl, (50, 50), SizeMethod.SIZE_BASED)
    gui3.set_border_color((0, 255, 0))

    print(gui3.topl)
    wind.handle_event(pygame.MOUSEBUTTONDOWN, ButtonClicked)

    wind.render()

main()
