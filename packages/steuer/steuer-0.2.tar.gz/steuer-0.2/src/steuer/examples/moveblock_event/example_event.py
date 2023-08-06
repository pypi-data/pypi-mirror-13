import time

import pygame

from src import steuer


# call back functions. They will be called when the mapped actions happened
def dpad_top_pressed(controller):
    """
    Callback function that is triggered, when the dpad top button was pressed

    :param controller:              the controller that triggered the action
    :type controller:               steuer.Controller
    """
    print("ACTION:" + str(controller.number) + ":" + controller.name + ":DPAD Top pressed")
    worms[controller.number].direction = TOP


def dpad_down_pressed(controller):
    """
    Callback function that is triggered, when the dpad down button was pressed

    :param controller:              the controller that triggered the action
    :type controller:               steuer.Controller
    """
    print("ACTION:" + str(controller.number) + ":" + controller.name + ":DPAD Down pressed")
    worms[controller.number].direction = DOWN


def dpad_left_pressed(controller):
    """
    Callback function that is triggered, when the dpad left button was pressed

    :param controller:              the controller that triggered the action
    :type controller:               steuer.Controller
    """
    print("ACTION:" + str(controller.number) + ":" + controller.name + ":DPAD Left pressed")
    worms[controller.number].direction = LEFT


def dpad_right_pressed(controller):
    """
    Callback function that is triggered, when the dpad right button was pressed

    :param controller:              the controller that triggered the action
    :type controller:               steuer.Controller
    """
    print("ACTION:" + str(controller.number) + ":" + controller.name + ":DPAD Right pressed")
    worms[controller.number].direction = RIGHT


def button_top_pressed(controller):
    """
    Callback function that is triggered, when the top button was pressed

    :param controller:              the controller that triggered the action
    :type controller:               steuer.Controller
    """
    print("ACTION:" + str(controller.number) + ":" + controller.name + ":Button Top pressed")
    worms[controller.number].direction = STOPPED


# Event callback functions for the controller configuration
# ======================================================================================================
def on_initialized():
    """
    Callback function that is triggered, when the initialization is finished
    """
    print("EVENT:" + "Steuer initialized")
    print("----------- Initialization -------")
    if steuer.mapping_databases['default'].found_database:
        print("Steuer mapping database found and loaded")
    else:
        print("No mapping database found. A new one will be created")


# Detection events
def on_detection_finished():
    """
    Callback function that is triggered, when the detection of connected controllers is complete
    """
    print("EVENT:" + "controller detection finished")
    print("----------- Detection ------------")
    print("{0} controllers found".format(steuer.controllers.__len__()))
    for controller in steuer.controllers:
        if controller.is_mapped:
            print("controller {0}:{1} was found in the mapping database and its events are mapped to actions".format(controller.number, controller.name))
        else:
            print("controller {0}:{1} was not found in mapping database".format(controller.number, controller.name))


# Mapping events
def on_controller_mapped(controller):
    """
    Callback function that is triggered, when the mapping of a controller was found

    :param controller:              the controller that should be mapped
    :type controller:               steuer.Controller
    """
    print("EVENT:" + "controller {0}:{1} mapped".format(controller.number, controller.name))


def on_mapping_not_found(controller):
    """
    Callback function that is triggered, when the mapping of a controller was not found

    :param controller:              the controller that should be mapped
    :type controller:               steuer.Controller
    """
    print("EVENT:" + "controller {0}:{1} could not be mapped. Controller name unknown.".format(controller.number, controller.name))


# Configuration events
def on_start_configuration():
    """
    Callback function that is triggered, when the configuration of all undetected controllers starts
    """
    print("EVENT:" + "Start configuration of unknown controller types")


def on_configuration_finished():
    """
    Callback function that is triggered, when the configuration of all undetected controllers is complete
    """
    print("EVENT:" + "All controllers are configured")


# Configuration mapping events
def on_mapping_configuration_init(controller):
    """
    Callback function that is triggered, when the configuration of a controller starts

    :param controller:              the controller that should be configured
    :type controller:               steuer.Controller
    """
    print("EVENT:" + "Start configure controller type :{0}".format(controller.name))


def on_mapping_configuration_finished(controller):
    """
    Callback function that is triggered, when the configuration of a controller is complete

    :param controller:              the controller that was configured
    :type controller:               steuer.Controller
    """
    print("EVENT:" + "controller type {0} configuration finished".format(controller.name))


# Map mapping events
def on_request_action(controller, action2configure):
    """
    Callback function that is triggered, when a new action should be configured

    :param action2configure:        the action to configure
    :type action2configure:         steuer.Action
    :param controller:              the controller from which an action should be requested
    :type controller:               steuer.Controller
    """
    print("EVENT:" + "Controller " + str(controller.number) + ": " + action2configure.long_name)


def on_event_mapped(controller, action2configure):
    """
    Callback function that is triggered, when an event was mapped

    :param action2configure:        the action that was mapped
    :type action2configure:         steuer.Action
    :param controller:              the controller the event was requested from
    :type controller:               steuer.Controller
    """
    print("EVENT:" + "Controller {0}:{1} - action:{2} mapped".format(controller.number, controller.name, action2configure.action))


def on_event_already_mapped(controller, action2configure):
    """
    Callback function that is triggered, when an event was already mapped to another action

    :param action2configure:        the action that was already mapped
    :type action2configure:         steuer.Action
    :param controller:              the controller the event was requested from
    :type controller:               steuer.Controller
    """
    print("EVENT:" + "Error: Controller {0}:{1} - action {2} already mapped".format(controller.number, controller.name, action2configure.action))


def on_wait(controller):
    """
    Callback function that is triggered in the wait cycles after the mapping. Here a waiting message could be set

    :param controller:              the controller that is waiting
    :type controller:               steuer.Controller
    """
    time.sleep(0.1)
    print("EVENT:" + "Controller {0}:{1} - is waiting".format(controller.number, controller.name))


# initialize pygame
# ======================================================================================================
pygame.init()
pygame.joystick.init()

# Set configuration event callback functions
# ======================================================================================================
# Stage events
steuer.Configuration.on_detection_finished = on_detection_finished
steuer.Configuration.on_mapping_not_found = on_mapping_not_found

# Mapping events
steuer.Controller.on_controller_mapped = on_controller_mapped

# Configuration events
steuer.on_initialized = on_initialized
steuer.on_start_configuration = on_start_configuration
steuer.on_configuration_finished = on_configuration_finished

# Configuration mapping events
steuer.Controller.on_mapping_configuration_init = on_mapping_configuration_init
steuer.Controller.on_mapping_configuration_finished = on_mapping_configuration_finished

# Action events
steuer.Action.on_request_action = on_request_action
steuer.Action.on_event_mapped = on_event_mapped
steuer.Action.on_event_already_mapped = on_event_already_mapped
steuer.Action.on_wait = on_wait

# Set action callback functions
steuer.Action('DPAD_TOP', 1, 'DPad top', 'Top', dpad_top_pressed)
steuer.Action('DPAD_DOWN', 2, 'DPad down', 'Down', dpad_down_pressed)
steuer.Action('DPAD_LEFT', 4, 'DPad left', 'Left', dpad_left_pressed)
steuer.Action('DPAD_RIGHT', 8, 'DPad right', 'Right', dpad_right_pressed)
steuer.Action('BUTTON_TOP', 2048, 'Button top', 'BTop', button_top_pressed)
steuer.Action('BUTTON_DOWN', 4096, 'Button down', 'BDown')
steuer.Action('BUTTON_LEFT', 8192, 'Button left', 'BLeft')
steuer.Action('BUTTON_RIGHT', 16384, 'Button right', 'BRight')
steuer.Action('SHOULDER_L1', 32768, 'Shoulder L1', 'L1')
steuer.Action('SHOULDER_L2', 65536, 'Shoulder L2', 'L2')
steuer.Action('SHOULDER_R1', 131072, 'Shoulder R1', 'R1')
steuer.Action('SHOULDER_R2', 262144, 'Shoulder R2', 'R2')
steuer.Action('ANALOG_L3', 524288, 'Analog L3', 'L3')
steuer.Action('ANALOG_R3', 1048576, 'Analog R3', 'R3')
steuer.Action('BUTTON_START', 2097152, 'Button start', 'BStart')
steuer.Action('BUTTON_SELECT', 4194304, 'Button select', 'BSelect')

# Set direction callback functions
steuer.Direction('DPAD_TOP', 0b0001, 'DPad top', 'Top')
steuer.Direction('DPAD_DOWN', 0b0010, 'DPad down', 'Down')
steuer.Direction('DPAD_LEFT', 0b0100, 'DPad left', 'Left')
steuer.Direction('DPAD_RIGHT', 0b1000, 'DPad right', 'Right')
steuer.Direction('DPAD_TOPLEFT', 0b0101, 'DPad top', 'Top Left')
steuer.Direction('DPAD_TOPRIGHT', 0b1001, 'DPad down', 'Down Right')
steuer.Direction('DPAD_DOWNLEFT', 0b0110, 'DPad down left', 'Down Left')
steuer.Direction('DPAD_DOWNRIGHT', 0b1010, 'DPad down right', 'Down Right')

# Module init
steuer.init()

# detect connected controllers
steuer.detect_connected_controllers()

# test if there exist unmapped controllers
if steuer.Configuration.undetected_controllers:
    # unmapped controllers exists
    # initialize unknown mapping configuration
    steuer.Configuration.init_undetected_controller_configuration()

    # Iterate unmapped controllers
    for _controller in steuer.Configuration.undetected_controllers:
        # search mapping again in the mapping database
        _mapping = steuer.Configuration.get_mapping_if_already_configured(_controller)

        # test if the mapping exist in the mapping database
        if _mapping is None:
            # the mapping was not found in mapping database
            # initialize controller configuration
            steuer.Configuration.init_mapping(_controller)

            # Iterate unconfigured actions
            for action in steuer.Action.unconfigured_actions:
                # initialize event detection
                action.init_event_detection(_controller)

                # test if action is configured
                while not action.status == steuer.Action.status_configured:
                    if action.status == action.status_delayed:
                        # Iterate delay mapping (5 Times)
                        action.delay_mapping(_controller)
                    elif action.status == steuer.Action.status_test_remapping:
                        # if the event is unmapped, map it to an action
                        # otherwise reset status to unconfigured
                        if action.is_event_unmapped(_controller) is True:
                            action.map_event(_controller)
                    else:
                        # get pygame event
                        for event in pygame.event.get():
                            if action.status == steuer.Action.status_unconfigured:
                                # detect event
                                action.detect_event(_controller, event)
                            elif action.status == steuer.Action.status_waiting:
                                # wait for trigger release
                                action.wait_for_trigger_release(event)

            # The mapping is saved to the mapping database
            _mapping = steuer.Configuration.exit_mapping(_controller)

        # set the controller mapping
        _controller.set_mapping(_mapping)

    # exit unknown mapping configuration
    steuer.Configuration.exit_undetected_controller_configuration()

# constants
# --------------------------------------------------------------
STOPPED = 0
LEFT = 1
TOP = 2
RIGHT = 3
DOWN = 4


# player object
# --------------------------------------------------------------
class Worm(pygame.sprite.Sprite):
    def __init__(self, initial_position, color):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface([7, 7])
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.topleft = initial_position
        self.direction = STOPPED

    def update(self):
        if self.direction == LEFT:
            if self.rect.left > 0:
                self.rect.left -= 1
            else:
                self.rect.left = 800

        if self.direction == TOP:
            if self.rect.top > 0:
                self.rect.top -= 1
            else:
                self.rect.top = 600

        if self.direction == RIGHT:
            if self.rect.left < 800:
                self.rect.left += 1
            else:
                self.rect.left = 0

        if self.direction == DOWN:
            if self.rect.top < 600:
                self.rect.top += 1
            else:
                self.rect.top = 0

    def render(self):
        screen.blit(self.image, self.rect)


# initialize variables
# --------------------------------------------------------------
worm_colors = [(255, 0, 0), (255, 40, 0), (255, 80, 0), (255, 120, 0), (255, 160, 0), (255, 200, 0), (255, 240, 0), (255, 255, 0)]
start_positions = [[0, 0], [40, 40], [80, 80], [120, 120], [160, 160], [200, 200], [240, 240], [280, 280]]
worms = []
is_running = True
number_of_players = 8

for player in range(0, number_of_players):
    worms.append(Worm(start_positions[player], worm_colors[player]))

# initialize pygame
# --------------------------------------------------------------
screen = pygame.display.set_mode([800, 600])
clock = pygame.time.Clock()

# main loop
# --------------------------------------------------------------
while is_running:
    clock.tick(60)

    # loop over events
    for event in pygame.event.get():
        # test if program should quit
        if event.type == pygame.QUIT:
            is_running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                is_running = False

            if event.key == pygame.K_UP:
                worms[0].direction = TOP
            if event.key == pygame.K_DOWN:
                worms[0].direction = DOWN
            if event.key == pygame.K_LEFT:
                worms[0].direction = LEFT
            if event.key == pygame.K_RIGHT:
                worms[0].direction = RIGHT

        else:
            # map event to actions
            # ==================================================
            steuer.call_event_and_direction(event)

    # update objects
    # ----------------------------------------------------------
    for worm in worms:
        worm.update()

    # render
    # ----------------------------------------------------------
    screen.fill([0, 0, 0])  # blank the screen.

    for worm in worms:
        worm.render()

    pygame.display.update()
