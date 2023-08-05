import IGUI
import pygame
from math import trunc

# This class will handle creating GUI interfaces with scroll bars

# This class is designed to allow the library user a fair bit of color and size customization of different elements of the window.
# Because of this, please check the documentation of this class for better information on different aspects of this class
class Scroll_Win(IGUI.BaseGUI):

    # The boundary surface where all the content can be drawn
    content_boundary = 0

    content = 0
    # Holds all the content created, as well as its position on the content_surface.
    # Information is ordered in this way:
    #   Identity:
    #       Content
    #       Start position
    identity_dict = {}
    # Determines where on the scroll window the scrollbar is rendered
    scroll_side = "right"
    # The width of the scrollbar's background
    bar_width = 10
    # The width of the scrollbar's background border
    out_border_size = 1
    # The color of the scrollbar's background
    bar_bg_color = (255, 255, 255)
    # The color of the scrollbar's background border
    out_border_color = (150, 150, 150)
    # The color of the scrollbar
    bar_color = (0, 0, 0)
    # The color of the scrollbar's border
    in_border_color = (100, 100, 100)
    # The color of the content window's background
    content_bg_color = (255, 255, 255)
    # The color of the content window's border
    content_border_color = (50, 50, 50)
    # The size of the scrollbar's border
    in_border_size = 1
    # The spacing between the scrollbar and the content window
    bar_content_spacing = 3
    # The size of the scrollbar as a fraction of its height over its maximum height
    bar_start_pos = (0, 0)
    bar_end_pos = (1, 1)

    content_boundary_start_pos = (0, 0)
    content_boundary_end_pos = (1, 1)

    content_dimensions = (0, 0)

    scroll_start_pos = (0, 0)
    scroll_dimensions = (bar_width - out_border_size, 1)

    def create_bar(self):

        y_dim = 1
        if self.scrollbar_bg.height - self.out_border_size - self.in_border_size - (self.content.height - self.height) > 10:
            y_dim = self.scrollbar_bg.height - self.out_border_size - self.in_border_size - (self.content.height - self.height)
        else:
            y_dim = 10

        self.scroll_dimensions = (self.bar_width, y_dim)
        self.scrollbar = IGUI.BaseGUI(self.scroll_start_pos, self.scroll_dimensions, self.in_border_size, 1)
        self.scrollbar.set_bg_color(self.bar_color)
        self.scrollbar.set_border_color(self.in_border_color)
        self.scrollbar.render(self.scrollbar_bg.Surface)
        self.scrollbar_bg.render(self.Surface)

    def scroll(self, direction):
        new_mouse_pos = pygame.mouse.get_pos()

    def create_content(self):

        self.content_boundary = IGUI.BaseGUI(self.content_boundary_start_pos, self.content_boundary_end_pos, 10)
        self.content_boundary.set_bg_color(self.content_bg_color)
        self.content_boundary.set_border_color(self.content_border_color)

        self.content_boundary = IGUI.BaseGUI(self.content_boundary.rel_topl, self.content_end_pos, 10)

        for content in self.identity_dict.keys():
            self.content.Surface.blit(self.identity_dict[content][0], self.identity_dict[content][1])
        self.content.render(self.content_boundary.Surface)
        self.content_boundary.render(self.Surface)

    # Creates the scroll bar
    # NOTE TO SELF: Separate certain sections of this function into their own functions
    def initialize_bar(self):

        if self.scroll_side == "right":
            self.bar_start_pos = (self.rel_in_topr[0] - self.bar_width, self.rel_in_topr[1])
            self.bar_dimensions = (self.bar_width, self.height - 2*self.border_size)

            self.content_start_pos = self.rel_in_topl
            self.content_end_pos = (self.rel_in_topr[0] - self.bar_width - self.bar_content_spacing, self.rel_in_bottomr[1])

        elif self.scroll_side == "left":
            self.bar_start_pos = self.rel_in_topl
            self.bar_dimensions = (self.bar_width, self.height - 2*self.border_size)

            self.content_start_pos = (self.rel_in_topl[0] + self.bar_width + self.bar_content_spacing, self.rel_in_topl[1])
            self.content_end_pos = self.rel_in_bottomr

        elif self.scroll_side == "top":
            self.bar_start_pos = self.rel_in_topl
            self.bar_dimensions = (self.width - 2*self.border_size, self.bar_width)

            self.content_start_pos = (self.rel_in_topl[0], self.rel_in_topl[1] + self.bar_width + self.bar_content_spacing)
            self.content_end_pos = self.rel_in_bottomr

        elif self.scroll_side == "bottom":
            self.bar_start_pos = (self.rel_in_bottoml[0], self.rel_in_bottomr[1] - self.bar_width - self.bar_content_spacing)
            self.bar_dimensions = (self.width - 2*self.border_size, self.bar_width)

            self.content_start_pos = self.rel_in_topl
            self.content_end_pos = (self.rel_in_bottomr[0], self.rel_in_bottomr[1] - self.bar_width)

        self.scrollbar_bg = IGUI.BaseGUI(self.bar_start_pos, self.bar_dimensions, self.out_border_size, 1)
        self.scrollbar_bg.set_bg_color(self.bar_bg_color)
        self.scrollbar_bg.set_border_color(self.in_border_color)

    # Reference IGUI.py for parameter types not listed
    def __init__(self, startpoint, endpoint, scroll_side = ("right"), width = 0, sizing_method=0):

        self.border_size = trunc(width)
        self.topleft = (trunc(startpoint[0]), trunc(startpoint[1]))

        self.determine_size(startpoint, endpoint, sizing_method)
        self.determine_coords()

        self.Surface = pygame.Surface((self.width, self.height))

        self.scroll_side = scroll_side

        self.draw_border()
        self.draw_corners()
        self.initialize_bar()
        self.create_content()
        self.create_bar()

    # Add content to the scroll window
    # @type content -> anything that can be blitted to a surface
    # @type pos -> Tuple (2 integers)
    # @type identity -> String or Integer (recommended)
    # DESIGN CHOICE: The purpose of the identity is to allow the user to remove or modify content after creating it using a unique ID
    def add_content(self, identity, content, pos):

        if pos[0] > self.content.width:
            self.content.size = (pos[0] + 10, self.content.size[1])
        if pos[1] > self.content.height:
            self.content.size = (self.content.size[0], pos[1] + 10)

        self.identity_dict[identity] = (content, pos)

    # Delete content from the scroll window
    # @type identity -> String or Integer
    # DESIGN CHOICE: The purpose of the identity is to allow the user to remove or modify content after creating it using a unique ID
    def remove_content(self, identity):
        if identity in self.identity_dict:
            del self.identity_dict[identity]

    # Render the scroll menu and its content
    # @type window -> Surface
    def render(self, window):
        self.draw_border()
        self.draw_corners()
        self.initialize_bar()
        self.create_content()
        self.create_bar()
        window.blit(self.Surface, self)

    # Sets the width of the entire scrollbar
    # @type width -> Integer
    def set_bar_width(self, width):
        self.bar_width = width

    def set_out_border_width(self, width):
        self.out_border_size = width

    def set_bar_bg_color(self, color):
        self.bar_bg_color = color

    def set_out_border_color(self, color):
        self.out_border_color = color

    def set_bar_color(self, color):
        self.bar_color = color

    def set_in_border_color(self, color):
        self.in_border_color = color

    def set_out_border_color(self, color):
        self.out_border_color = color

    def set_bg_color(self, color):
        self.content.set_bg_color(color)




