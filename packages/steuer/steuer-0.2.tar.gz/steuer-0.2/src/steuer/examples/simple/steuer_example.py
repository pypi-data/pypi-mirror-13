import time
import pygame
import steuer


# call back functions. They will be called when the mapped actions happened
# ======================================================================================================
def dpad_top_pressed(controller):
    """
    Callback function that is triggered, when the dpad top button was pressed

    :param controller:              the controller that triggered the action
    :type controller:               steuer.Controller
    """
    print("ACTION:" + str(controller.number) + ":" + controller.name + ":DPAD Top pressed")


def dpad_down_pressed(controller):
    """
    Callback function that is triggered, when the dpad down button was pressed

    :param controller:              the controller that triggered the action
    :type controller:               steuer.Controller
    """
    print("ACTION:" + str(controller.number) + ":" + controller.name + ":DPAD Down pressed")


def dpad_left_pressed(controller):
    """
    Callback function that is triggered, when the dpad left button was pressed

    :param controller:              the controller that triggered the action
    :type controller:               steuer.Controller
    """
    print("ACTION:" + str(controller.number) + ":" + controller.name + ":DPAD Left pressed")


def dpad_right_pressed(controller):
    """
    Callback function that is triggered, when the dpad right button was pressed

    :param controller:              the controller that triggered the action
    :type controller:               steuer.Controller
    """
    print("ACTION:" + str(controller.number) + ":" + controller.name + ":DPAD Right pressed")


def button_top_pressed(controller):
    """
    Callback function that is triggered, when the top button was pressed

    :param controller:              the controller that triggered the action
    :type controller:               steuer.Controller
    """
    print("ACTION:" + str(controller.number) + ":" + controller.name + ":Button Top pressed")


def button_down_pressed(controller):
    """
    Callback function that is triggered, when the down button was pressed

    :param controller:              the controller that triggered the action
    :type controller:               steuer.Controller
    """
    print("ACTION:" + str(controller.number) + ":" + controller.name + ":Button Down pressed")


def button_left_pressed(controller):
    """
    Callback function that is triggered, when the left button was pressed

    :param controller:              the controller that triggered the action
    :type controller:               steuer.Controller
    """
    print("ACTION:" + str(controller.number) + ":" + controller.name + ":Button Left pressed")


def button_right_pressed(controller):
    """
    Callback function that is triggered, when the right button was pressed

    :param controller:              the controller that triggered the action
    :type controller:               steuer.Controller
    """
    print("ACTION:" + str(controller.number) + ":" + controller.name + ":Button Right pressed")


def shoulder_l1_pressed(controller):
    """
    Callback function that is triggered, when the shoulder button L1 was pressed

    :param controller:              the controller that triggered the action
    :type controller:               steuer.Controller
    """
    print("ACTION:" + str(controller.number) + ":" + controller.name + ":Shoulder L1 pressed")


def shoulder_l2_pressed(controller):
    """
    Callback function that is triggered, when the shoulder button L2 was pressed

    :param controller:              the controller that triggered the action
    :type controller:               steuer.Controller
    """
    print("ACTION:" + str(controller.number) + ":" + controller.name + ":Shoulder L2 pressed")


def shoulder_r1_pressed(controller):
    """
    Callback function that is triggered, when the shoulder button R1 was pressed

    :param controller:              the controller that triggered the action
    :type controller:               steuer.Controller
    """
    print("ACTION:" + str(controller.number) + ":" + controller.name + ":Shoulder R1 pressed")


def shoulder_r2_pressed(controller):
    """
    Callback function that is triggered, when the shoulder button R2 was pressed

    :param controller:              the controller that triggered the action
    :type controller:               steuer.Controller
    """
    print("ACTION:" + str(controller.number) + ":" + controller.name + ":Shoulder R2 pressed")


def analog_l3_pressed(controller):
    """
    Callback function that is triggered, when the left stick button was pressed

    :param controller:              the controller that triggered the action
    :type controller:               steuer.Controller
    """
    print("ACTION:" + str(controller.number) + ":" + controller.name + ":Analog L3 pressed")


def analog_r3_pressed(controller):
    """
    Callback function that is triggered, when the right stick button was pressed

    :param controller:              the controller that triggered the action
    :type controller:               steuer.Controller
    """
    print("ACTION:" + str(controller.number) + ":" + controller.name + ":Analog R3 pressed")


def button_start_pressed(controller):
    """
    Callback function that is triggered, when the start button was pressed

    :param controller:              the controller that triggered the action
    :type controller:               steuer.Controller
    """
    print("ACTION:" + str(controller.number) + ":" + controller.name + ":Button Start pressed")


def button_select_pressed(controller):
    """
    Callback function that is triggered, when the select button was pressed

    :param controller:              the controller that triggered the action
    :type controller:               steuer.Controller
    """
    print("ACTION:" + str(controller.number) + ":" + controller.name + ":Button Select pressed")


def dpad_top_released(controller):
    """
    Callback function that is triggered, when the dpad top button was released

    :param controller:              the controller that triggered the action
    :type controller:               steuer.Controller
    """
    print("ACTION:" + str(controller.number) + ":" + controller.name + ":DPAD Top released")


def dpad_down_released(controller):
    """
    Callback function that is triggered, when the dpad down button was released

    :param controller:              the controller that triggered the action
    :type controller:               steuer.Controller
    """
    print("ACTION:" + str(controller.number) + ":" + controller.name + ":DPAD Down released")


def dpad_left_released(controller):
    """
    Callback function that is triggered, when the dpad left button was released

    :param controller:              the controller that triggered the action
    :type controller:               steuer.Controller
    """
    print("ACTION:" + str(controller.number) + ":" + controller.name + ":DPAD Left released")


def dpad_right_released(controller):
    """
    Callback function that is triggered, when the dpad right button was released

    :param controller:              the controller that triggered the action
    :type controller:               steuer.Controller
    """
    print("ACTION:" + str(controller.number) + ":" + controller.name + ":DPAD Right released")


def button_top_released(controller):
    """
    Callback function that is triggered, when the top button was released

    :param controller:              the controller that triggered the action
    :type controller:               steuer.Controller
    """
    print("ACTION:" + str(controller.number) + ":" + controller.name + ":Button Top released")


def button_down_released(controller):
    """
    Callback function that is triggered, when the down button was released

    :param controller:              the controller that triggered the action
    :type controller:               steuer.Controller
    """
    print("ACTION:" + str(controller.number) + ":" + controller.name + ":Button Down released")


def button_left_released(controller):
    """
    Callback function that is triggered, when the left button was released

    :param controller:              the controller that triggered the action
    :type controller:               steuer.Controller
    """
    print("ACTION:" + str(controller.number) + ":" + controller.name + ":Button Left released")


def button_right_released(controller):
    """
    Callback function that is triggered, when the right button was released

    :param controller:              the controller that triggered the action
    :type controller:               steuer.Controller
    """
    print("ACTION:" + str(controller.number) + ":" + controller.name + ":Button Right released")


def shoulder_l1_released(controller):
    """
    Callback function that is triggered, when the shoulder button L1 was released

    :param controller:              the controller that triggered the action
    :type controller:               steuer.Controller
    """
    print("ACTION:" + str(controller.number) + ":" + controller.name + ":Shoulder L1 released")


def shoulder_l2_released(controller):
    """
    Callback function that is triggered, when the shoulder button L2 was released

    :param controller:              the controller that triggered the action
    :type controller:               steuer.Controller
    """
    print("ACTION:" + str(controller.number) + ":" + controller.name + ":Shoulder L2 released")


def shoulder_r1_released(controller):
    """
    Callback function that is triggered, when the shoulder button R1 was released

    :param controller:              the controller that triggered the action
    :type controller:               steuer.Controller
    """
    print("ACTION:" + str(controller.number) + ":" + controller.name + ":Shoulder R1 released")


def shoulder_r2_released(controller):
    """
    Callback function that is triggered, when the shoulder button R2 was released

    :param controller:              the controller that triggered the action
    :type controller:               steuer.Controller
    """
    print("ACTION:" + str(controller.number) + ":" + controller.name + ":Shoulder R2 released")


def analog_l3_released(controller):
    """
    Callback function that is triggered, when the left stick button was released

    :param controller:              the controller that triggered the action
    :type controller:               steuer.Controller
    """
    print("ACTION:" + str(controller.number) + ":" + controller.name + ":Analog L3 released")


def analog_r3_released(controller):
    """
    Callback function that is triggered, when the right stick button was released

    :param controller:              the controller that triggered the action
    :type controller:               steuer.Controller
    """
    print("ACTION:" + str(controller.number) + ":" + controller.name + ":Analog R3 released")


def button_start_released(controller):
    """
    Callback function that is triggered, when the start button was released

    :param controller:              the controller that triggered the action
    :type controller:               steuer.Controller
    """
    print("ACTION:" + str(controller.number) + ":" + controller.name + ":Button Start released")


def button_select_released(controller):
    """
    Callback function that is triggered, when the select button was released

    :param controller:              the controller that triggered the action
    :type controller:               steuer.Controller
    """
    print("ACTION:" + str(controller.number) + ":" + controller.name + ":Button Select released")


def dpad_top_heading(controller):
    """
    Callback function that is triggered, when the direction top was pressed

    :param controller:              the controller that triggered the action
    :type controller:               steuer.Controller
    """
    print("DIRECTION:" + str(controller.number) + ":" + controller.name + ":DPAD Top heading")


def dpad_down_heading(controller):
    """
    Callback function that is triggered, when the direction down was pressed

    :param controller:              the controller that triggered the action
    :type controller:               steuer.Controller
    """
    print("DIRECTION:" + str(controller.number) + ":" + controller.name + ":DPAD Down heading")


def dpad_left_heading(controller):
    """
    Callback function that is triggered, when the direction left was pressed

    :param controller:              the controller that triggered the action
    :type controller:               steuer.Controller
    """
    print("DIRECTION:" + str(controller.number) + ":" + controller.name + ":DPAD Left heading")


def dpad_right_heading(controller):
    """
    Callback function that is triggered, when the direction right was pressed

    :param controller:              the controller that triggered the action
    :type controller:               steuer.Controller
    """
    print("DIRECTION:" + str(controller.number) + ":" + controller.name + ":DPAD Right heading")


def dpad_topleft_heading(controller):
    """
    Callback function that is triggered, when the direction top left was pressed

    :param controller:              the controller that triggered the action
    :type controller:               steuer.Controller
    """
    print("DIRECTION:" + str(controller.number) + ":" + controller.name + ":DPAD Top Left heading")


def dpad_topright_heading(controller):
    """
    Callback function that is triggered, when the direction top right was pressed

    :param controller:              the controller that triggered the action
    :type controller:               steuer.Controller
    """
    print("DIRECTION:" + str(controller.number) + ":" + controller.name + ":DPAD Top Right heading")


def dpad_downleft_heading(controller):
    """
    Callback function that is triggered, when the direction down left was pressed

    :param controller:              the controller that triggered the action
    :type controller:               steuer.Controller
    """
    print("DIRECTION:" + str(controller.number) + ":" + controller.name + ":DPAD Down Left heading")


def dpad_downright_heading(controller):
    """
    Callback function that is triggered, when the direction down right was pressed

    :param controller:              the controller that triggered the action
    :type controller:               steuer.Controller
    """
    print("DIRECTION:" + str(controller.number) + ":" + controller.name + ":DPAD Down Right heading")


def dpad_top_unheading(controller):
    """
    Callback function that is triggered, when the direction top was released

    :param controller:              the controller that triggered the action
    :type controller:               steuer.Controller
    """
    print("DIRECTION:" + str(controller.number) + ":" + controller.name + ":DPAD Top unheading")


def dpad_down_unheading(controller):
    """
    Callback function that is triggered, when the direction down was released

    :param controller:              the controller that triggered the action
    :type controller:               steuer.Controller
    """
    print("DIRECTION:" + str(controller.number) + ":" + controller.name + ":DPAD Down unheading")


def dpad_left_unheading(controller):
    """
    Callback function that is triggered, when the direction left was released

    :param controller:              the controller that triggered the action
    :type controller:               steuer.Controller
    """
    print("DIRECTION:" + str(controller.number) + ":" + controller.name + ":DPAD Left unheading")


def dpad_right_unheading(controller):
    """
    Callback function that is triggered, when the direction right was released

    :param controller:              the controller that triggered the action
    :type controller:               steuer.Controller
    """
    print("DIRECTION:" + str(controller.number) + ":" + controller.name + ":DPAD Right unheading")


def dpad_topleft_unheading(controller):
    """
    Callback function that is triggered, when the direction top left was released

    :param controller:              the controller that triggered the action
    :type controller:               steuer.Controller
    """
    print("DIRECTION:" + str(controller.number) + ":" + controller.name + ":DPAD Top Left unheading")


def dpad_topright_unheading(controller):
    """
    Callback function that is triggered, when the direction top right was released

    :param controller:              the controller that triggered the action
    :type controller:               steuer.Controller
    """
    print("DIRECTION:" + str(controller.number) + ":" + controller.name + ":DPAD Top Right unheading")


def dpad_downleft_unheading(controller):
    """
    Callback function that is triggered, when the direction down left was released

    :param controller:              the controller that triggered the action
    :type controller:               steuer.Controller
    """
    print("DIRECTION:" + str(controller.number) + ":" + controller.name + ":DPAD Down Left unheading")


def dpad_downright_unheading(controller):
    """
    Callback function that is triggered, when the direction down right was released

    :param controller:              the controller that triggered the action
    :type controller:               steuer.Controller
    """
    print("DIRECTION:" + str(controller.number) + ":" + controller.name + ":DPAD Down Right unheading")


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
@classmethod
def on_detection_finished(cls):
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
@classmethod
def on_controller_mapped(cls,controller):
    """
    Callback function that is triggered, when the mapping of a controller was found

    :param controller:              the controller that should be mapped
    :type controller:               steuer.Controller
    """
    print("EVENT:" + "controller {0}:{1} mapped".format(controller.number, controller.name))


@classmethod
def on_mapping_not_found(cls,controller):
    """
    Callback function that is triggered, when the mapping of a controller was not found

    :param controller:              the controller that should be mapped
    :type controller:               steuer.Controller
    """
    print("EVENT:" + "controller {0}:{1} could not be mapped. Controller name unknown.".format(controller.number, controller.name))


# Configuration events
@classmethod
def on_start_configuration(cls):
    """
    Callback function that is triggered, when the configuration of all undetected controllers starts
    """
    print("EVENT:" + "Start configuration of unknown controller types")


@classmethod
def on_configuration_finished(cls):
    """
    Callback function that is triggered, when the configuration of all undetected controllers is complete
    """
    print("EVENT:" + "All controllers are configured")


# Configuration mapping events
@classmethod
def on_mapping_configuration_init(cls,controller):
    """
    Callback function that is triggered, when the configuration of a controller starts

    :param controller:              the controller that should be configured
    :type controller:               steuer.Controller
    """
    print("EVENT:" + "Start configure controller type :{0}".format(controller.name))


@classmethod
def on_mapping_configuration_finished(cls,controller):
    """
    Callback function that is triggered, when the configuration of a controller is complete

    :param controller:              the controller that was configured
    :type controller:               steuer.Controller
    """
    print("EVENT:" + "controller type {0} configuration finished".format(controller.name))


# Map mapping events
@classmethod
def on_request_action(cls,controller, action2configure):
    """
    Callback function that is triggered, when a new action should be configured

    :param action2configure:        the action to configure
    :type action2configure:         steuer.Action
    :param controller:              the controller from which an action should be requested
    :type controller:               steuer.Controller
    """
    print("EVENT:" + "Controller " + str(controller.number) + ": " + action2configure.long_name)


@classmethod
def on_event_mapped(cls,controller, action2configure):
    """
    Callback function that is triggered, when an event was mapped

    :param action2configure:        the action that was mapped
    :type action2configure:         steuer.Action
    :param controller:              the controller the event was requested from
    :type controller:               steuer.Controller
    """
    print("EVENT:" + "Controller {0}:{1} - action:{2} mapped".format(controller.number, controller.name, action2configure.action))


@classmethod
def on_event_already_mapped(cls,controller, action2configure):
    """
    Callback function that is triggered, when an event was already mapped to another action

    :param action2configure:        the action that was already mapped
    :type action2configure:         steuer.Action
    :param controller:              the controller the event was requested from
    :type controller:               steuer.Controller
    """
    print("EVENT:" + "Error: Controller {0}:{1} - action {2} already mapped".format(controller.number, controller.name, action2configure.action))


@classmethod
def on_wait(cls,controller):
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
steuer.Action('DPAD_TOP', 1, 'DPad top', 'Top', dpad_top_pressed, dpad_top_released),
steuer.Action('DPAD_DOWN', 2, 'DPad down', 'Down', dpad_down_pressed, dpad_down_released),
steuer.Action('DPAD_LEFT', 4, 'DPad left', 'Left', dpad_left_pressed, dpad_left_released),
steuer.Action('DPAD_RIGHT', 8, 'DPad right', 'Right', dpad_right_pressed, dpad_right_released),
steuer.Action('BUTTON_TOP', 2048, 'Button top', 'BTop', button_top_pressed, button_top_released),
steuer.Action('BUTTON_DOWN', 4096, 'Button down', 'BDown', button_down_pressed, button_down_released),
steuer.Action('BUTTON_LEFT', 8192, 'Button left', 'BLeft', button_left_pressed, button_left_released),
steuer.Action('BUTTON_RIGHT', 16384, 'Button right', 'BRight', button_right_pressed, button_right_released),
steuer.Action('SHOULDER_L1', 32768, 'Shoulder L1', 'L1', shoulder_l1_pressed, shoulder_l1_released),
steuer.Action('SHOULDER_L2', 65536, 'Shoulder L2', 'L2', shoulder_l2_pressed, shoulder_l2_released),
steuer.Action('SHOULDER_R1', 131072, 'Shoulder R1', 'R1', shoulder_r1_pressed, shoulder_r1_released),
steuer.Action('SHOULDER_R2', 262144, 'Shoulder R2', 'R2', shoulder_r2_pressed, shoulder_r2_released),
steuer.Action('ANALOG_L3', 524288, 'Analog L3', 'L3', analog_l3_pressed, analog_l3_released),
steuer.Action('ANALOG_R3', 1048576, 'Analog R3', 'R3', analog_r3_pressed, analog_r3_released),
steuer.Action('BUTTON_START', 2097152, 'Button start', 'BStart', button_start_pressed, button_start_released),
steuer.Action('BUTTON_SELECT', 4194304, 'Button select', 'BSelect', button_select_pressed, button_select_released),

# Set direction callback functions
# ======================================================================================================
steuer.Direction('DPAD_TOP', 0b0001, 'DPad top', 'Top', dpad_top_heading, dpad_top_unheading),
steuer.Direction('DPAD_DOWN', 0b0010, 'DPad down', 'Down', dpad_down_heading, dpad_down_unheading),
steuer.Direction('DPAD_LEFT', 0b0100, 'DPad left', 'Left', dpad_left_heading, dpad_left_unheading),
steuer.Direction('DPAD_RIGHT', 0b1000, 'DPad right', 'Right', dpad_right_heading, dpad_right_unheading),
steuer.Direction('DPAD_TOPLEFT', 0b0101, 'DPad top', 'Top Left', dpad_topleft_heading, dpad_topleft_unheading),
steuer.Direction('DPAD_TOPRIGHT', 0b1001, 'DPad down', 'Down Right', dpad_topright_heading, dpad_topright_unheading),
steuer.Direction('DPAD_DOWNLEFT', 0b0110, 'DPad down left', 'Down Left', dpad_downleft_heading, dpad_downleft_unheading),
steuer.Direction('DPAD_DOWNRIGHT', 0b1010, 'DPad down right', 'Down Right', dpad_downright_heading, dpad_downright_unheading),

# Module initialization
# ======================================================================================================
steuer.init()

# Controller detection and configuration
# ======================================================================================================
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

# Print out the detected actions and movements
# ======================================================================================================
print("")
print("---------------------------------------------------------------------------------------")
print("*                                 use your controllers                                *")
print("---------------------------------------------------------------------------------------")
print("")

# Main loop
is_running = True

while is_running:
    # set frame rate
    pygame.time.Clock().tick(25)

    # loop over events
    for event in pygame.event.get():
        # test if program should quit
        if event.type == pygame.QUIT:
            is_running = False

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            is_running = False

        # map events to actions
        # ==============================================================================================
        steuer.call_event_and_direction(event)

    # print the controller bits
    # ==================================================================================================
    for controller_number in range(0, pygame.joystick.get_count()):
        print(steuer.controllers[controller_number].name + ": " + str(steuer.controllers[controller_number].bits))