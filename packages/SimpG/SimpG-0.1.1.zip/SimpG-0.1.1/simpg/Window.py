import Errors
import pygame
from Igui import Igui
from TreeRoot import TreeRoot

pygame.display.init()

# This class is a singleton. Only ONE window may be created. Attempting to create more will raise an exception.
class Window(Igui, TreeRoot,):

    exists = False
    SURFACE = None # Window Surface
    event_list = [] # All events

    @classmethod
    def handle_error(cls):
        raise Errors.SingletonException(str(cls))

    # When handle event is called, the program will respond to an event

    # event -> The pygame event that should be responded to
    # cond -> Any additional conditions that should be met before responding to the condition
    # func -> The function that should be called if event occurs, and cond returns true
    # parameters -> a list of parameters for the function to operate on
    def handle_event(self, event, func, cond=True, ):
        self.event_list.append((event, func, cond))

    def render_children(self):

        all_nodes = self.get_descendants()
        all_nodes.reverse()

        for gui in all_nodes:
            gui[1].update_surface()

        for gui in all_nodes:
            gui[1].render(gui[0])

    def render(self):

        while True:
            self.render_children()
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return

                for event_request in self.event_list:
                    if event.type == event_request[0] and event_request[2]:
                        event_request[1]()


    def __init__(self, resolution):
        if Window.exists == True:
            self.handle_error()
            del self
            return

        self.SURFACE = pygame.display.set_mode(resolution)
        Window.exists = True
        self.size = resolution







