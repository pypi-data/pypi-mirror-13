import json  # used for import and export the controller library
import pygame  # the controller framework
import os  # used to read and write files
import logging  # used for logging
import logging.config  # the logging configuration

__author__ = "ThorN ^ Pionierwerk <thorsten.butschke@googlemail.com>"

# Steuer
# ==========================================================================
# Module to handle connected controllers:
# - Detect connected controllers
# - Map unknown controller buttons and axis to supported functions
# - Save and load mappings to and from a json file
# ==========================================================================
# Global variables
# ==========================================================================

# internal flags
_flags = {}

# the list of mapping databases
mapping_databases = {}

# pygame detected controllers
controllers = []

# Initialize logging
# **************************************************************************
# load logger config
logging.config.fileConfig('logging.conf')
# create logger
logger = logging.getLogger('Steuer')

# Event callback
# **************************************************************************
# module initialized
on_initialized = None

# constants that symbolize the meaning of the controller bits
# @formatter:off
DPAD_TOP = 0b1                              # bit 0:    DPAD TOP
DPAD_DOWN = 0b10                            # bit 1:    DPAD Down
DPAD_LEFT = 0b100                           # bit 2:    DPAD Left
DPAD_RIGHT = 0b1000                         # bit 3:    DPAD Right
LEFT_STICK_TOP = 0b10000                    # bit 4:    Left Stick Top - Todo: For future releases
LEFT_STICK_DOWN = 0b100000                  # bit 5:    Left Stick Down - Todo: For future releases
LEFT_STICK_LEFT = 0b1000000                 # bit 6:    Left Stick Left - Todo: For future releases
LEFT_STICK_RIGHT = 0b10000000               # bit 7:    Left Stick Right - Todo: For future releases
RIGHT_STICK_TOP = 0b100000000               # bit 8:    Right Stick Top - Todo: For future releases
RIGHT_STICK_DOWN = 0b1000000000             # bit 9:    Right Stick Down - Todo: For future releases
RIGHT_STICK_LEFT = 0b10000000000            # bit 10:   Right Stick Left - Todo: For future releases
RIGHT_STICK_RIGHT = 0b100000000000          # bit 11:   Right Stick Right - Todo: For future releases
BUTTON_TOP = 0b1000000000000                # bit 12:   Button Top
BUTTON_DOWN = 0b10000000000000              # bit 13:   Button Down
BUTTON_LEFT = 0b100000000000000             # bit 14:   Button Left
BUTTON_RIGHT = 0b1000000000000000           # bit 15:   Button Right
SHOULDER_L1 = 0b10000000000000000           # bit 16:   Shoulder L1
SHOULDER_L2 = 0b100000000000000000          # bit 17:   Shoulder L2
SHOULDER_R1 = 0b1000000000000000000         # bit 18:   Shoulder R1
SHOULDER_R2 = 0b10000000000000000000        # bit 19:   Shoulder R2
ANALOG_L3 = 0b100000000000000000000         # bit 20:   Left Stick Button (L3)
ANALOG_R3 = 0b1000000000000000000000        # bit 21:   Right Stick Button (R3)
BUTTON_START = 0b10000000000000000000000    # bit 22:   Button Start
BUTTON_SELECT = 0b100000000000000000000000  # bit 23:   Button Select
BUTTON_HOME = 0b1000000000000000000000000   # bit 24:   Button Home - Todo: For future releases
# @formatter:on

dpad_bit_mask = 0b1111  # bits 0-3
left_stick_bit_mask = 0b11110000  # bits 4-7  - Todo: For future releases
rstick_bit_mask = 0b111100000000  # bits 8-11 - Todo: For future releases


# functions
# ==========================================================================
def init(database_name="default", filename="steuer.json", mappingdb_path=os.path.join(os.path.expanduser("~"), ".steuer"), use_events=True):
    """
    initialize the module.
    Triggers the "on_initialized" event

    :param database_name:               The alias of the mapping database. 'default' is the default mapping database
    :type database_name:                string
    :param filename:                    The name of the mapping database. Default name is "steuer.json"
    :type filename:                     string
    :param mappingdb_path:              Path to the mapping database. The default path "" points to the directory of the module
    :type mappingdb_path:               string
    :param use_events:                  Defines if the event triggering functionality is used
    :type use_events:                   bool
    """
    _flags['use_events'] = use_events

    logger.debug("Steuer initializing")
    logger.debug("searching database in %s", mappingdb_path)

    # try to load the mapping database
    # if not found the mapping database is an empty array
    mapping_databases[database_name] = MappingDB(database_name, filename, mappingdb_path)
    # get the number of controllers
    _number_of_connected_controllers = pygame.joystick.get_count()
    logger.debug("%s controllers found", str(_number_of_connected_controllers))

    # create a Controller entity for every connected controller
    for controller_number in range(0, _number_of_connected_controllers):
        _controller = Controller(controller_number)
        controllers.append(_controller)

    # trigger the "on_initialized" event
    if on_initialized is not None and _flags['use_events']:
        on_initialized()


def detect_connected_controllers(database_name="default"):
    """
    Wrapper of MappingDB.detect_connected_controllers

    :param database_name:               The alias of the mapping database. 'default' is the default mapping database
    :type database_name:                string
    """
    Configuration.detect_connected_controllers(mapping_databases[database_name])


def get_mapping_by_controller(controller, database_name="default"):
    """
    Wrapper of MappingDB.get_mapping_by_controller

    :param controller:                  The controller that should be searched in the mapping database
    :type controller:                   steuer.Controller
    :param database_name:               The alias of the mapping database. 'default' is the default mapping database
    :type database_name:                string
    :return                             If a mapping was found the mapping is returned, if not None will be returned
    :rtype                              dict
    """
    return MappingDB.get_mapping_by_controller(mapping_databases[database_name], controller)


def call_event_and_direction(event):
    """
    Calls the action mapped to an pygame event if one is defined. Also calls the direction callback function, if one is defined
    Set the controller bits.
    Returns the action that was mapped to the event.

    :param event:                       The pygame event
    :type event                         pygame.Event
    :return                             the action that happened
    :rtype                              string
    """
    _action_happened = None

    if event.type == pygame.JOYBUTTONDOWN:
        _controller_number = event.dict["joy"]
        _button = str(event.dict["button"])

        # use event data to find the mapping
        if _button in controllers[_controller_number].mapping["button"].keys():
            # get action
            _action_happened = controllers[_controller_number].mapping["button"][_button]["Function"]

            # set controller bits
            # get old and new direction
            _old_direction = controllers[_controller_number].bits & dpad_bit_mask
            _new_direction = controllers[_controller_number].change_bits(Action.actions[_action_happened].value, True) & dpad_bit_mask

            # if the action has an callback function, call this callback function
            if Action.actions[_action_happened].on_pressed is not None:
                Action.actions[_action_happened].on_pressed(controllers[_controller_number])

            # call direction on_heading & on_unheading
            if not _old_direction == 0 and Action.directions[str(_old_direction)].on_unheading is not None:
                Action.directions[str(_old_direction)].on_unheading(controllers[_controller_number])
            if not _new_direction == 0 and Action.directions[str(_new_direction)].on_heading is not None:
                Action.directions[str(_new_direction)].on_heading(controllers[_controller_number])

    elif event.type == pygame.JOYBUTTONUP:
        _controller_number = event.dict["joy"]
        _button = str(event.dict["button"])

        # use event data to find the mapping
        if _button in controllers[_controller_number].mapping["button"].keys():
            # get action
            _action_happened = controllers[_controller_number].mapping["button"][_button]["Function"]

            # clear controller bits
            # get old and new direction
            _old_direction = controllers[_controller_number].bits & dpad_bit_mask
            _new_direction = controllers[_controller_number].change_bits(Action.actions[_action_happened].value, False) & dpad_bit_mask

            # if action has an callback function, call this callback function
            if not Action.actions[_action_happened].on_released is None:
                Action.actions[_action_happened].on_released(controllers[_controller_number])

            # call direction on_heading & on_unheading
            if not _old_direction == 0 and not Action.directions[str(_old_direction)].on_unheading is None:
                Action.directions[str(_old_direction)].on_unheading(controllers[_controller_number])
            if not _new_direction == 0 and not Action.directions[str(_new_direction)].on_heading is None:
                Action.directions[str(_new_direction)].on_heading(controllers[_controller_number])

    if event.type == pygame.JOYAXISMOTION:
        _controller_number = event.dict["joy"]
        _value = event.dict["value"]
        _axis = str(event.dict["axis"])
        _key_part = str(_axis) + ":"
        _key = _key_part

        if _value <= -1 or _value >= 1:
            if _value > 0:
                _key += ">"
            else:
                _key += "<"

            # use event to find the mapping
            if _key in controllers[_controller_number].mapping["axis"].keys():
                # get action
                _action_happened = controllers[_controller_number].mapping["axis"][_key]["Function"]

                # set controller bits
                # get old and new direction
                _old_direction = controllers[_controller_number].bits & dpad_bit_mask
                _new_direction = controllers[_controller_number].change_bits(Action.actions[_action_happened].value, True) & dpad_bit_mask

                # if action has an callback function, call this callback function
                if not Action.actions[_action_happened].on_pressed is None:
                    Action.actions[_action_happened].on_pressed(controllers[_controller_number])

                # call direction on_heading & on_unheading
                if not _old_direction == 0 and not Action.directions[str(_old_direction)].on_unheading is None:
                    Action.directions[str(_old_direction)].on_unheading(controllers[_controller_number])
                if not _new_direction == 0 and not Action.directions[str(_new_direction)].on_heading is None:
                    Action.directions[str(_new_direction)].on_heading(controllers[_controller_number])

                # save action as last axis action
                controllers[_controller_number].set_last_axis_action(_axis, _action_happened)
        else:
            if not controllers[_controller_number].get_last_axis_action(_axis) is None:
                # react on the center the axis event
                # get last axis action
                _action_happened = controllers[_controller_number].get_last_axis_action(_axis)

                # clear controller bits
                # get old and new direction
                _old_direction = controllers[_controller_number].bits & dpad_bit_mask
                _new_direction = controllers[_controller_number].change_bits(Action.actions[_action_happened].value, False) & dpad_bit_mask

                # if last axis action has an callback function, call this callback function
                if not Action.actions[_action_happened].on_released is None:
                    Action.actions[_action_happened].on_released(controllers[_controller_number])

                # call direction on_heading & on_unheading
                if not _old_direction == 0 and not Action.directions[str(_old_direction)].on_unheading is None:
                    Action.directions[str(_old_direction)].on_unheading(controllers[_controller_number])
                if not _new_direction == 0 and not Action.directions[str(_new_direction)].on_heading is None:
                    Action.directions[str(_new_direction)].on_heading(controllers[_controller_number])

                # save action as last axis action
                controllers[_controller_number].set_last_axis_action(_axis)

    if event.type == pygame.JOYHATMOTION:
        _controller_number = event.dict["joy"]
        _value_x = event.dict["value"][0]
        _value_y = event.dict["value"][1]
        _hat = event.dict["hat"]
        _key_vertical = str(_hat) + ":" + str(_value_x) + ":0"
        _key_horizontal = str(_hat) + ":0:" + str(_value_y)
        _action_vertical_happened = None
        _action_horizontal_happened = None

        # get old direction
        _old_direction = controllers[_controller_number].bits & dpad_bit_mask
        _new_direction = _old_direction

        # 8 way movement
        # detection of 8 directions and 8 actions (top,
        # ******************************************************************************************************
        # Todo: to detect real hat movement test if action is configured for 8 way movement.

        # 4 way movement
        # detection of 8 directions and 4 actions (left,right,top,down only)
        # a action for the each direction (top-down, left-right) is calculated. Based on these two events,
        # directions (top-left,top-right,down-left,down-right) are calculated
        # ******************************************************************************************************
        # get last actions
        _last_hat_vertical_action = controllers[_controller_number].get_last_hat_action(_hat, 'vertical')
        _last_hat_horizontal_action = controllers[_controller_number].get_last_hat_action(_hat, 'horizontal')

        # use event to find the mapping
        # get action
        if _key_vertical in controllers[_controller_number].mapping["hat"].keys():
            _action_vertical_happened = controllers[_controller_number].mapping["hat"][_key_vertical]["Function"]
            _action_happened = _action_horizontal_happened

        if _key_horizontal in controllers[_controller_number].mapping["hat"].keys():
            _action_horizontal_happened = controllers[_controller_number].mapping["hat"][_key_horizontal]["Function"]
            _action_happened = _action_horizontal_happened

        # trigger on_release events and clear direction bits
        if _last_hat_vertical_action is not None and not _action_vertical_happened == _last_hat_vertical_action:
            # get new direction and clear controller bits
            _new_direction = controllers[_controller_number].change_bits(Action.actions[_last_hat_vertical_action].value, False)

            # call callback function
            if Action.actions[_last_hat_vertical_action].on_released is not None:
                Action.actions[_last_hat_vertical_action].on_released(controllers[_controller_number])

            # set last hat action
            controllers[_controller_number].set_last_hat_action(_hat, 'vertical')

        if _last_hat_horizontal_action is not None and not _action_horizontal_happened == _last_hat_horizontal_action:
            # get new direction and clear controller bits
            _new_direction = controllers[_controller_number].change_bits(Action.actions[_last_hat_horizontal_action].value, False)

            # call callback function
            if Action.actions[_last_hat_horizontal_action].on_released is not None:
                Action.actions[_last_hat_horizontal_action].on_released(controllers[_controller_number])

            # set last hat action
            controllers[_controller_number].set_last_hat_action(_hat, 'horizontal')

        # trigger new action and set new direction
        if _action_vertical_happened is not None and not _action_vertical_happened == _last_hat_vertical_action:
            # get new direction and set controller bits
            _new_direction = controllers[_controller_number].change_bits(Action.actions[_action_vertical_happened].value, True)

            # call callback function
            if Action.actions[_action_vertical_happened].on_pressed is not None:
                Action.actions[_action_vertical_happened].on_pressed(controllers[_controller_number])

            # set last hat action
            controllers[_controller_number].set_last_hat_action(_hat, 'vertical', _action_vertical_happened)

        if _action_horizontal_happened is not None and not _action_horizontal_happened == _last_hat_horizontal_action:
            # get new direction and set controller bits
            _new_direction = controllers[_controller_number].change_bits(Action.actions[_action_horizontal_happened].value, True)

            # call callback function
            if Action.actions[_action_horizontal_happened].on_pressed is not None:
                Action.actions[_action_horizontal_happened].on_pressed(controllers[_controller_number])

            # set last hat action
            controllers[_controller_number].set_last_hat_action(_hat, 'horizontal', _action_horizontal_happened)

        # call direction on_heading and on_unheading
        if _old_direction != _new_direction:
            if not _old_direction == 0 and not Action.directions[str(_old_direction)].on_unheading is None:
                Action.directions[str(_old_direction)].on_unheading(controllers[_controller_number])
            if not _new_direction == 0 and not Action.directions[str(_new_direction)].on_heading is None:
                Action.directions[str(_new_direction)].on_heading(controllers[_controller_number])

    return _action_happened


def call_event(event):
    """
    Calls the action mapped to an pygame event if one is defined.
    Set the controller bits.
    Returns the action that was mapped to the event.

    :param event:                       The pygame event
    :type event                         pygame.Event
    :return                             the action that happened
    :rtype                              string
    """
    _action_happened = None

    if "joy" in event.dict:
        _controller_number = event.dict["joy"]

        if controllers[_controller_number].mapping is not None:
            if event.type == pygame.JOYBUTTONDOWN:
                _button = str(event.dict["button"])

                # use event data to find the mapping
                if _button in controllers[_controller_number].mapping["button"].keys():
                    # get action
                    _action_happened = controllers[_controller_number].mapping["button"][_button]["Function"]

                    # set controller bits
                    controllers[_controller_number].change_bits(Action.actions[_action_happened].value, True) & dpad_bit_mask

                    # if the action has an callback function, call this callback function
                    if Action.actions[_action_happened].on_pressed is not None:
                        Action.actions[_action_happened].on_pressed(controllers[_controller_number])

            elif event.type == pygame.JOYBUTTONUP:
                _button = str(event.dict["button"])

                # use event data to find the mapping
                if _button in controllers[_controller_number].mapping["button"].keys():
                    # get action
                    _action_happened = controllers[_controller_number].mapping["button"][_button]["Function"]

                    # clear controller bits
                    controllers[_controller_number].change_bits(Action.actions[_action_happened].value, False) & dpad_bit_mask

                    # if action has an callback function, call this callback function
                    if not Action.actions[_action_happened].on_released is None:
                        Action.actions[_action_happened].on_released(controllers[_controller_number])

            elif event.type == pygame.JOYAXISMOTION:
                _value = event.dict["value"]
                _axis = str(event.dict["axis"])
                _key_part = str(_axis) + ":"
                _key = _key_part

                if _value <= -1 or _value >= 1:
                    if _value > 0:
                        _key += ">"
                    else:
                        _key += "<"

                    # use event to find the mapping
                    if _key in controllers[_controller_number].mapping["axis"].keys():
                        # get action
                        _action_happened = controllers[_controller_number].mapping["axis"][_key]["Function"]

                        # set controller bits
                        controllers[_controller_number].change_bits(Action.actions[_action_happened].value, True) & dpad_bit_mask

                        # if action has an callback function, call this callback function
                        if not Action.actions[_action_happened].on_pressed is None:
                            Action.actions[_action_happened].on_pressed(controllers[_controller_number])

                        # save action as last axis action
                        controllers[_controller_number].set_last_axis_action(_axis, _action_happened)
                else:
                    if not controllers[_controller_number].get_last_axis_action(_axis) is None:
                        # react on the center the axis event

                        # get last axis action
                        _action_happened = controllers[_controller_number].get_last_axis_action(_axis)

                        # clear controller bits
                        controllers[_controller_number].change_bits(Action.actions[_action_happened].value, False) & dpad_bit_mask

                        # if last axis action has an callback function, call this callback function
                        if not Action.actions[_action_happened].on_released is None:
                            Action.actions[_action_happened].on_released(controllers[_controller_number])

                        # save action as last axis action
                        controllers[_controller_number].set_last_axis_action(_axis)

            elif event.type == pygame.JOYHATMOTION:
                _value_x = event.dict["value"][0]
                _value_y = event.dict["value"][1]
                _hat = event.dict["hat"]
                _key_vertical = str(_hat) + ":" + str(_value_x) + ":0"
                _key_horizontal = str(_hat) + ":0:" + str(_value_y)

                _action_vertical_happened = None
                _action_horizontal_happened = None

                # 8 way movement
                # detection of 8 directions and 8 actions (top,
                # ******************************************************************************************************
                # Todo: to detect real hat movement test if action is configured for 8 way movement.

                # 4 way movement
                # detection of 8 directions and 4 actions (left,right,top,down only)
                # a action for the each direction (top-down, left-right) is calculated. Based on these two events,
                # directions (top-left,top-right,down-left,down-right) are calculated
                # ******************************************************************************************************
                # get last actions
                _last_hat_vertical_action = controllers[_controller_number].get_last_hat_action(_hat, 'vertical')
                _last_hat_horizontal_action = controllers[_controller_number].get_last_hat_action(_hat, 'horizontal')

                # use event to find the mapping
                # get action
                if _key_vertical in controllers[_controller_number].mapping["hat"].keys():
                    _action_vertical_happened = controllers[_controller_number].mapping["hat"][_key_vertical]["Function"]
                    _action_happened = _action_horizontal_happened

                if _key_horizontal in controllers[_controller_number].mapping["hat"].keys():
                    _action_horizontal_happened = controllers[_controller_number].mapping["hat"][_key_horizontal]["Function"]
                    _action_happened = _action_horizontal_happened

                # trigger on_release events and clear direction bits
                if _last_hat_vertical_action is not None and not _action_vertical_happened == _last_hat_vertical_action:
                    # clear controller bits
                    controllers[_controller_number].change_bits(Action.actions[_last_hat_vertical_action].value, False)

                    # call on_released action
                    Action.actions[_last_hat_vertical_action].on_released(controllers[_controller_number])
                    controllers[_controller_number].set_last_hat_action(_hat, 'vertical')
                if _last_hat_horizontal_action is not None and not _action_horizontal_happened == _last_hat_horizontal_action:
                    # clear controller bits
                    controllers[_controller_number].change_bits(Action.actions[_last_hat_horizontal_action].value, False)

                    # call on_released action
                    Action.actions[_last_hat_horizontal_action].on_released(controllers[_controller_number])
                    controllers[_controller_number].set_last_hat_action(_hat, 'horizontal')

                # trigger new action and set new direction
                if _action_vertical_happened is not None and not _action_vertical_happened == _last_hat_vertical_action:
                    # set controller bits
                    controllers[_controller_number].change_bits(Action.actions[_action_vertical_happened].value, True)

                    # call on_pressed action
                    if Action.actions[_action_vertical_happened].on_pressed is not None:
                        Action.actions[_action_vertical_happened].on_pressed(controllers[_controller_number])

                    # set last hat action
                    controllers[_controller_number].set_last_hat_action(_hat, 'vertical', _action_vertical_happened)
                if _action_horizontal_happened is not None and not _action_horizontal_happened == _last_hat_horizontal_action:
                    # set controller bits
                    controllers[_controller_number].change_bits(Action.actions[_action_horizontal_happened].value, True)

                    # call on_pressed action
                    if Action.actions[_action_horizontal_happened].on_pressed is not None:
                        Action.actions[_action_horizontal_happened].on_pressed(controllers[_controller_number])

                    # set last hat action
                    controllers[_controller_number].set_last_hat_action(_hat, 'horizontal', _action_horizontal_happened)

    return _action_happened


def get_action(event):
    """
    Set the controller bits.
    Returns the action that was mapped to the event.

    :param event:                       The pygame event
    :type event                         pygame.Event
    :return                             the action that happened
    :rtype                              string
    """
    _action_happened = None

    if "joy" in event.dict:
        _controller_number = event.dict["joy"]

        if controllers[_controller_number].mapping is not None:
            if event.type == pygame.JOYBUTTONDOWN:
                _button = str(event.dict["button"])

                # use event data to find the mapping
                if _button in controllers[_controller_number].mapping["button"].keys():
                    # get action
                    _action_happened = controllers[_controller_number].mapping["button"][_button]["Function"]

                    # set controller bits
                    controllers[_controller_number].change_bits(Action.actions[_action_happened].value, True)

            elif event.type == pygame.JOYBUTTONUP:
                _controller_number = event.dict["joy"]
                _button = str(event.dict["button"])

                # use event data to find the mapping
                if _button in controllers[_controller_number].mapping["button"].keys():
                    # get action
                    _action_happened = controllers[_controller_number].mapping["button"][_button]["Function"]

                    # clear controller bits
                    controllers[_controller_number].change_bits(Action.actions[_action_happened].value, False)

                    _action_happened = None

            elif event.type == pygame.JOYAXISMOTION:
                _value = event.dict["value"]
                _axis = str(event.dict["axis"])
                _key_part = str(_axis) + ":"
                _key = _key_part

                if _value <= -1 or _value >= 1:
                    if _value > 0:
                        _key += ">"
                    else:
                        _key += "<"

                    # use event to find the mapping
                    if _key in controllers[_controller_number].mapping["axis"].keys():
                        # get action
                        _action_happened = controllers[_controller_number].mapping["axis"][_key]["Function"]

                        # set controller bits
                        controllers[_controller_number].change_bits(Action.actions[_action_happened].value, True)

                        # save action as last axis action
                        controllers[_controller_number].set_last_axis_action(_axis, _action_happened)
                else:
                    if not controllers[_controller_number].get_last_axis_action(_axis) is None:
                        # react on the center the axis event
                        # get last axis action
                        _action_happened = controllers[_controller_number].get_last_axis_action(_axis)

                        # clear controller bits
                        controllers[_controller_number].change_bits(Action.actions[_action_happened].value, False)

                        # save action as last axis action
                        controllers[_controller_number].set_last_axis_action(_axis)

            elif event.type == pygame.JOYHATMOTION:
                _value_x = event.dict["value"][0]
                _value_y = event.dict["value"][1]
                _hat = event.dict["hat"]
                _key_vertical = str(_hat) + ":" + str(_value_x) + ":0"
                _key_horizontal = str(_hat) + ":0:" + str(_value_y)
                _action_vertical_happened = None
                _action_horizontal_happened = None

                # get last actions
                _last_hat_vertical_action = controllers[_controller_number].get_last_hat_action(_hat, 'vertical')
                _last_hat_horizontal_action = controllers[_controller_number].get_last_hat_action(_hat, 'horizontal')

                # use event to find the mapping
                # get action
                if _key_vertical in controllers[_controller_number].mapping["hat"].keys():
                    _action_vertical_happened = controllers[_controller_number].mapping["hat"][_key_vertical]["Function"]
                    _action_happened = _action_vertical_happened

                if _key_horizontal in controllers[_controller_number].mapping["hat"].keys():
                    _action_horizontal_happened = controllers[_controller_number].mapping["hat"][_key_horizontal]["Function"]
                    _action_happened = _action_horizontal_happened

                # clear controller bits
                if _last_hat_vertical_action is not None and not _action_vertical_happened == _last_hat_vertical_action:
                    controllers[_controller_number].change_bits(Action.actions[_last_hat_vertical_action].value, False)
                    controllers[_controller_number].set_last_hat_action(_hat, 'vertical')
                if _last_hat_horizontal_action is not None and not _action_horizontal_happened == _last_hat_horizontal_action:
                    controllers[_controller_number].change_bits(Action.actions[_last_hat_horizontal_action].value, False)
                    controllers[_controller_number].set_last_hat_action(_hat, 'horizontal')

                # set controller bits
                if _action_vertical_happened is not None and not _action_vertical_happened == _last_hat_vertical_action:
                    controllers[_controller_number].change_bits(Action.actions[_action_vertical_happened].value, True)
                    controllers[_controller_number].set_last_hat_action(_hat, 'vertical', _action_vertical_happened)
                if _action_horizontal_happened is not None and not _action_horizontal_happened == _last_hat_horizontal_action:
                    controllers[_controller_number].change_bits(Action.actions[_action_horizontal_happened].value, True)
                    controllers[_controller_number].set_last_hat_action(_hat, 'horizontal', _action_horizontal_happened)

    return _action_happened


# class that represent the MappingDB. The MappingDB is a collection
# of mapped controller types. Mapping and controller type is a synonym
# =====================================================================
class MappingDB(object):
    def __init__(self, database_name, filename, mappingdb_path):
        """
        Construct.
        Set the path to the mapping database. And load the mapping database

        :param database_name:           The alias of the mapping database. 'default' is the default mapping database
        :type database_name:            string
        :param filename:                The name of the file of the mapping database
        :type filename:                 string
        :param mappingdb_path:          The path to the mapping database
        :type filename:                 string
        """
        # @formatter:off
        self.database_name = database_name                  # alias of the database.
        self.path = ""                                      # the path to the database file
        self.mappings = {}                                  # the mappings in the database
        self.filename = filename                            # the name of the database file
        self.found_database = False                         # flag that show if the database was found (True) in the filesystem or not (False)
        self.folder_path = mappingdb_path                   # the path to the folder where the database file is in

        self.set_path(mappingdb_path)
        # @formatter:on

        self.load()

    def set_path(self, mappingdb_path):
        """
        set the path to the mapping database

        :param mappingdb_path:          The path to the mapping database
        :type mappingdb_path:           string
        """
        self.path = os.path.join(mappingdb_path, self.filename)

    def load(self):
        """
        loads the mapping database. If no mapping database is found, the mappings are an empty dict
        """
        if os.path.isfile(self.path):
            self.mappings = json.load(open(self.path))
            logger.info("Steuer mapping database found and loaded")
            self.found_database = True
        else:
            if not os.path.exists(self.folder_path):
                os.mkdir(self.folder_path)

            self.mappings = {}
            logger.warning("No mapping database found")

    def save(self):
        """
        write the complete mapping library to a json file
        """
        with open(self.path, 'w') as outfile:
            json.dump(self.mappings, outfile)
        outfile.close()

        logger.info("mapping file written to: %s", self.path)

    def add_mapping(self, controller):
        """
        save the mapping of the controller to the database

        :param controller:              The controller that has a mapping that should be saved
        :type controller:               steuer.Controller
        """
        _new_mapping = {controller.name: controller.mapping}

        logger.debug("new mapping configured for controller type:%s", controller.name)

        self.mappings.update(_new_mapping)
        self.save()

    def get_mapping_by_controller(self, controller):
        """
        Find a mapping by the name of the controller in the mapping database.
        If no mapping was found, the return is None

        :param controller:              The controller to find
        :type controller:               steuer.Controller
        :return:                        Mapping from the mapping database which key match the name of the controller.
        :rtype:                         dict

        """
        if controller.name in mapping_databases[self.database_name].mappings.keys():
            logger.info("controller %s:%s was found in mapping db and was configured", str(controller.number), controller.name)
            return mapping_databases[self.database_name].mappings[controller.name]
        else:
            logger.info("controller %s was not found in mapping db", controller.name)
            return None


# class that handle the configuration of an undetected controller
class Configuration(object):
    # Class attributes
    # *****************************************************************
    # controllers that could not be detected and later have to be configured
    undetected_controllers = []

    # Stages events
    # --------------------------------------------------------------------------
    # detection of controllers finished. All controllers where a mapping exists are mapped.
    on_detection_finished = None

    # Mapping events
    # -----------------------------------------------------------------
    # controller was not found in the mapping database
    on_mapping_not_found = None

    # Configuration mapping events
    # -----------------------------------------------------------------
    # Event that is triggered when a controller is selected to be configured
    on_mapping_configuration_init = None

    #  Event that is triggered when all actions are configured for a mapping
    on_mapping_configuration_finished = None

    # Configuration events
    # -----------------------------------------------------------------
    #  Event that is triggered when a new controller is selected to be configured
    on_start_configuration = None

    # Event that is triggered when all controllers that have to be configured are configured
    on_configuration_finished = None

    # Class functions
    # *****************************************************************
    @classmethod
    def detect_connected_controllers(cls, database):
        """
        Scan all connected controllers and try to get the mapping of the controller from the mapping database.
        If a mapping was found, the mapping of the controller is filled,
        If no mapping was found, the mapping of the controller is empty and the controller is saved in the unmapped controllers list
        Triggers the "on_detection_finished" event

        :param database:                the database to search in for the controllers
        :type database:                 steuer.MappingDB
        """
        for controller in controllers:
            # Try to find the controller by its name in the library
            # --------------------------------------------------------------
            _mapping = database.get_mapping_by_controller(controller)

            if _mapping is None:
                # No mapping was found and the controller is saved for later
                cls.mark_as_undetected(controller)
            else:
                # Controller was found
                # Add mapping to the connected controller mappings
                controllers[controller.number].set_mapping(_mapping)

        logger.debug("detection finished")

        # trigger the "on_detection_finished" event
        if cls.on_detection_finished is not None and _flags['use_events']:
            cls.on_detection_finished()

    @classmethod
    def init_undetected_controller_configuration(cls):
        """
        Initialize the configuration of undetected controllers
        Triggers the "on start configuration" event
        """
        logger.debug("start configuration of unknown controller types")

        # quit all controllers
        for controller in controllers:
            logger.debug("Controller {0}:{1} disabled".format(controller.number, controller.name))
            pygame.joystick.Joystick(controller.number).quit()

        # trigger the "on start configuration" event
        if cls.on_start_configuration is not None and _flags['use_events']:
            cls.on_start_configuration()

    @classmethod
    def exit_undetected_controller_configuration(cls):
        """
        Finish the configuration of undetected mappings
        Trigger the "on_configuration_finished" event
        """
        # remove all controllers from the unmapped controllers list
        del Configuration.undetected_controllers[:]

        # init all mapped controllers
        for controller in controllers:
            if controller.is_mapped:
                pygame.joystick.Joystick(controller.number).init()
                logger.debug("Controller {0}:{1} enabled".format(controller.number, controller.name))

        # trigger the "on_configuration_finished" event
        if cls.on_configuration_finished is not None and _flags['use_events']:
            cls.on_configuration_finished()

    @classmethod
    def init_mapping(cls, controller):
        """
        Enable the controller
        Trigger the "on_mapping_configuration_init" event

        :param controller:              the controller to be mapped
        :type:                          steuer.Controller
        """

        # initialize controller
        pygame.joystick.Joystick(controller.number).init()
        logger.debug("Controller {0}:{1} enabled".format(controller.number, controller.name))

        # initialize an empty mapping
        controller.mapping = {"button": {}, "axis": {}, "hat": {}}

        # trigger the "on_mapping_configuration_init" event
        if cls.on_mapping_configuration_init is not None and _flags['use_events']:
            cls.on_mapping_configuration_init(controller)

    @classmethod
    def exit_mapping(cls, controller, database_name="default"):
        """
        The mapping is saved into the mapping database.
        The controller is disabled.
        The "mapping configuration finished" event is triggered

        :param controller:              the controller that finished the mapping
        :type controller                steuer.Controller
        :param database_name:           the name of the mapping database where to look for the mapping.
        :type database_name             string
        :return:                        The now complete mapping of the controller
        :rtype:                         dict
        """
        # Put mapping into the library and save mapping db
        mapping_databases[database_name].add_mapping(controller)

        # quit controller
        pygame.joystick.Joystick(controller.number).quit()
        logger.debug("Controller {0}:{1} disabled".format(controller.number, controller.name))

        # trigger the "mapping configuration finished" event
        if cls.on_mapping_configuration_finished is not None and _flags['use_events']:
            cls.on_mapping_configuration_finished(controller)

        return controller.mapping

    @classmethod
    def mark_as_undetected(cls, controller):
        """
        Add a controller to the list of unmapped controllers
        Triggers the "mapping not found" event

        :param controller:              the controller to be marked as undetected
        :type controller:               steuer.Controller
        """
        cls.undetected_controllers.append(controller)

        # trigger the "mapping not found" event
        #if cls.on_mapping_not_found is not None and _flags['use_events']:
        cls.on_mapping_not_found(controller)

    @classmethod
    def get_mapping_if_already_configured(cls, controller, database_name="default"):
        """
        Try to get the mapping. This will be successful if the controller
        was already mapped during the configuration of a controller of the
        same controller type.

        :param controller               the controller to search for in the mapping database
        :type controller                steuer.Controller
        :param database_name:           the name of the mapping database where to look for the mapping.
        :type database_name             string
        :return                         The mapping of the controller
        :rtype                          dict
        """
        _mapping = mapping_databases[database_name].get_mapping_by_controller(controller)

        return _mapping


# class that represents a connected controller and the mapping
# =====================================================================
class Controller(object):
    # functions
    # *****************************************************************
    def __init__(self, controller_number):
        """
        Constructor. Initialize a controller based on the pygame controller number

        :param controller_number:       The pygame controller number
        :type controller_number:        int
        """
        # pygame controller initialization
        _controller = pygame.joystick.Joystick(controller_number)
        _controller.init()

        # @formatter:off
        self.is_mapped = False  # flag that shows if the controller is already mapped
        self.mapping = None  # the event to action mapping from the mapping database

        # get data of the controller from pygame
        self.name = _controller.get_name()  # the name of the controller type
        self.number = controller_number     # the pygame controller number
        self.bits = 0                       # bitfields that holds the information if an action is active or not. Values could be DPAD_TOP...,BUTTON_TOP...,LEFT_STICK_TOP... etc
        self._last_axis_action = {}         # The last axis action. Used to determine on_release and on_unheading actions.
                                            # The value will be a dictionary with axis number keys
        self._last_hat_action = {}          # The last hat actions. Used to determine  on_release and on_unheading actions.
                                            # The value will be an dictionary with 'vertical' and 'horizontal' keys
        # @formatter:on

        # Mapping events
        # -----------------------------------------------------------------
        # controller was successfully mapped
        self.on_controller_mapped = None

    def set_mapping(self, mapping):
        """
        Set the mapping of a controller
        Triggers the 'controller mapped' event

        :param mapping:                         The mapping
        :type mapping:                          dict
        """
        self.mapping = mapping
        self.is_mapped = True

        # trigger the 'controller mapped' event
        if self.on_controller_mapped is not None and _flags['use_events']:
            self.on_controller_mapped(self)

    def change_bits(self, value, add_value):
        """
        Change the heading bit.
        Depending on the add_value parameter the value is added to the heading bits (True)
        or the value is substracted from the heading bits (False)

        :param value:                   The value to add to the heading bits
        :type value:                    int
        :param add_value:               Flag to show it the value is added or substracted from the heading bits
        :type add_value:                bool
        :return:                        The heading bits
        :rtype:                         int
        """
        if add_value:
            self.bits += value
        else:
            self.bits -= value

        return self.bits

    def get_last_axis_action(self, axis):
        """
        Getter for the last axis action

        :param axis:                    The axis
        :type axis:                     string
        :return:                        The last axis action
        :rtype:                         steuer.Action
        """
        if axis not in self._last_axis_action:
            # There is no last axis action for the given axis
            return None
        else:
            return self._last_axis_action[axis]

    def set_last_axis_action(self, axis, action=None):
        """
        Setter for the last axis action

        :param axis:                    The axis
        :type axis:                     string
        :param action:                  The action to become the last axis action
        :type action:                   steuer.Action
        """
        self._last_axis_action[axis] = action

    def get_last_hat_action(self, hat, direction):
        """
        Getter for the last hat action

        :param hat:                     The hat
        :type hat:                      int
        :param direction:               Either 'vertical' or 'horizontal'
        :type direction                 string
        :return:                        The last hat action for the given direction
        :rtype:                         steuer.Action
        """
        _hat = str(hat)

        if _hat not in self._last_hat_action:
            # There is no last action for this hat
            return None
        else:
            if direction not in self._last_hat_action[_hat]:
                # There is no last action on this hat for the given direction
                return None
            else:
                return self._last_hat_action[_hat][direction]

    def set_last_hat_action(self, hat, direction, action=None):
        """
        Setter for the last hat actions

        :param hat:                     The hat
        :type hat:                      int
        :param direction:               Either 'vertical' or 'horizontal'
        :type direction                 string
        :param action:                  The action to become the last hat action for the given direction
        :type action:                   steuer.Action
        """
        _hat = str(hat)

        if _hat not in self._last_hat_action:
            # If there was no last action on this hat for the given direction before, a dictionary for the hat is created
            self._last_hat_action[_hat] = {}

        self._last_hat_action[_hat][direction] = action


# class to connect callback functions to a action-name that then could be
# mapped to a event of a controller
# =====================================================================
class Action(object):
    # class variables
    # *****************************************************************
    # @formatter:off
    unconfigured_actions = []   # Ordered list of actions to configure.
    actions = {}                # Actions dictionary. This dictionary will be used to get an action
                                # based on it's key from the mapping
    directions = {}             # List of directions
    status_unconfigured = 0     # action is no bound to an event
    status_waiting = 1          # the action mapping is waiting that the trigger of the event is released
    status_delayed = 2          # the action mapping is delayed without event processing to ensure, that the trigger is finally released
    status_test_remapping = 3   # action is bound to an event
    status_configured = 4       # action is bound to an event
    # @formatter:on

    # Event callback functions
    # *****************************************************************
    # Action events
    # -----------------------------------------------------------------
    #  Event that is triggered when an action is selected to configure
    on_request_action = None

    #  Event that is triggered when an action was successful configured
    on_event_already_mapped = None

    # Event that is triggered when an event was already mapped to an action
    on_event_mapped = None

    #  Event that is triggered during the idle loop after an action was configured
    on_wait = None

    # functions
    # *****************************************************************
    def __init__(self, action, value, long_name, short_name, on_pressed=None, on_released=None):
        """
        Action constructor.

        :param action:                      The name of the action. Your application will only get noticed of this name
        :type action:                       string
        :param value:                       The bit value of the direction if the action triggers a direction.
                                            1:  Top
                                            2:  Down
                                            4:  Left
                                            8:  Right
        :type value:                        int
        :param long_name:                   The long description. Use it to display messages
        :type long_name:                    string
        :param short_name:                  The short description. Use it to display status of actions. Examples: mapped, not mapped etc.
        :type short_name:                   string
        :param on_pressed:                  The callback function that is triggered when the button to trigger a action is pressed
        :type on_pressed:                   function
        :param on_released:                 The callback function that is triggered when the button that triggered an action is released
        :type on_released:                  function
        """
        # @formatter:off
        self.action = action                        # The name of the action
        self.value = value                          # The bit value of the direction if the action triggers a direction
        self.long_name = long_name                  # The long description
        self.short_name = short_name                # The short description
        self.on_pressed = on_pressed                # The callback function that is triggered when the button to trigger a action is pressed
        self.on_released = on_released              # The callback function that is triggered when the button that triggered an action is released
        self.mapped = False                         # Flag to show, if an action is already mapped
        self.event_is_mapped = False
        self.status = None                          # the status is used to determine the phases of the mapping
        self._configuration_mapping_key = None
        self._configuration_trigger_event = None    # the pygame event that triggers a configuration
        self._delay_counter = 5                     # counter how ofter a delay is called to ensure that the event is finally released
        # @formater:on

        Action.unconfigured_actions.append(self)
        Action.actions[self.action] = self

    def init_event_detection(self, controller):
        """
        Reset the status
        Triggers the "request action" event

        :param controller:              The controller the action is configured for
        :type controller:               steuer.Controller
        """
        # reset the status of the action to unconfigured
        self.status = Action.status_unconfigured
        self._delay_counter = 5

        # triggers the "request action" event
        if Action.on_request_action is not None and _flags['use_events']:
            Action.on_request_action(controller, self)

    def detect_event(self, controller, event):
        """
        Detect an event that could be mapped to an action

        :param controller:              The controller to configure
        :type controller:               steuer.Controller
        :param event:                   The pygame event to test if its a supported event
        :type event:                    pygame.Event
        """
        _detected = False

        if "joy" in event.dict:
            if event.dict["joy"] == controller.number:
                # Map a button event
                # --------------------------------------------------------
                if event.type == pygame.JOYBUTTONDOWN:
                    _detected = True
                # Map a axis event
                # --------------------------------------------------------
                elif event.type == pygame.JOYAXISMOTION and (event.dict["value"] <= -1 or event.dict["value"] >= 1):
                    _detected = True
                # Map a hat event
                # --------------------------------------------------------
                elif event.type == pygame.JOYHATMOTION and (event.dict["value"][0] != 0 or event.dict["value"][1] != 0):
                    _detected = True

        if _detected is True:
            self._configuration_trigger_event = event
            self.status = Action.status_waiting

    def wait_for_trigger_release(self, event):
        """
        Wait that the event that triggered the configuration is released. Then set the status to test_remapping

        :param event:                   The pygame event to test if its a Steuer supported event
        :type event:                    pygame.Event
        """
        _event_detected = False

        if "joy" in event.dict:
            if event.dict["joy"] == self._configuration_trigger_event.dict["joy"]:
                # wait that the button is released
                # --------------------------------------------------------
                if event.type == pygame.JOYBUTTONUP and self._configuration_trigger_event.type == pygame.JOYBUTTONDOWN:
                    _button = event.dict["button"]
                    _key = self._configuration_trigger_event.dict["button"]

                    # test if the event is the one that triggered the configuration
                    if _button == _key:
                        # save section
                        self._configuration_mapping_key = str(_key)
                        _event_detected = True

                # wait that a axis return the value 0, that means, that the axis is not moved anymore
                # --------------------------------------------------------
                elif event.type == pygame.JOYAXISMOTION and self._configuration_trigger_event.type == pygame.JOYAXISMOTION:
                    _axis = event.dict["axis"]
                    _value = event.dict["value"]
                    _axis_trigger = self._configuration_trigger_event.dict["axis"]
                    _value_trigger = self._configuration_trigger_event.dict["value"]

                    # test if the event is the one that triggered the configuration
                    if _axis == _axis_trigger and _value != _value_trigger:
                        if _value_trigger > 0.0:
                            _value_trigger = ">"
                        else:
                            _value_trigger = "<"

                        _key = str(_axis_trigger) + ":" + str(_value_trigger)

                        # save section
                        self._configuration_mapping_key = _key
                        _event_detected = True

                # wait that the hat is released
                # --------------------------------------------------------
                elif event.type == pygame.JOYHATMOTION and self._configuration_trigger_event.type == pygame.JOYHATMOTION:
                    _hat = str(event.dict["hat"])
                    _hat_trigger = str(self._configuration_trigger_event.dict["hat"])
                    _value_x = event.dict["value"][0]
                    _value_y = event.dict["value"][1]
                    _value_x_trigger = self._configuration_trigger_event.dict["value"][0]
                    _value_y_trigger = self._configuration_trigger_event.dict["value"][1]

                    # test if the event is the one that triggered the configuration  and the release event is of type central position
                    if _hat == _hat_trigger and _value_x == 0 and _value_y == 0:
                        _key = str(_hat_trigger) + ":" + str(_value_x_trigger) + ":" + str(_value_y_trigger)

                        # save section
                        self._configuration_mapping_key = _key
                        _event_detected = True

            if _event_detected is True:
                self.status = Action.status_test_remapping

    def is_event_unmapped(self, controller):
        """
        Test if the action is not already mapped.
        If it is already configured triggers the "event already mapped" event and reset the action status to unconfigured.
        If the event could be mapped set the action status to delayed

        :param controller:              The controller to configure
        :type controller:               steuer.Controller
        :return:                        True: Event could be mapped to an action. False: Event was already mapped
        :rtype:                         bool
        """
        _event_unmapped = True

        if self._configuration_trigger_event.type == pygame.JOYBUTTONDOWN:
            # Test a button event
            if self._configuration_mapping_key in controller.mapping['button'].keys():
                _event_unmapped = False
        elif self._configuration_trigger_event.type == pygame.JOYAXISMOTION:
            # Test a axis event
            if self._configuration_mapping_key in controller.mapping['axis'].keys():
                _event_unmapped = False
        elif self._configuration_trigger_event.type == pygame.JOYHATMOTION:
            # Test a hat event
            if self._configuration_mapping_key in controller.mapping['hat'].keys():
                _event_unmapped = False

        if _event_unmapped is True:
            # Action could now be mapped
            self.status = Action.status_delayed
            self.mapped = True

            logger.debug("Steuer action %s mapped", self.long_name)
        else:
            # Event was already mapped
            self.status = Action.status_unconfigured

            logger.warning("event already mapped")

            # trigger the "event already mapped" event
            if Action.on_event_already_mapped is not None and _flags['use_events']:
                Action.on_event_already_mapped(controller, self)

        return _event_unmapped

    def delay_mapping(self, controller):
        """
        Delay the configuration to ensure, that the triggered event is finally released
        Triggers the "wait" event

        :param controller:              The controller to configure
        :type controller:               steuer.Controller
        """
        # Clear pygame event queue
        pygame.event.clear()

        # trigger the "wait" event
        if Action.on_wait is not None and _flags['use_events']:
            Action.on_wait(controller)

        self._delay_counter -= 1

        if self._delay_counter == 0:
            self.status = Action.status_configured

    def map_event(self, controller):
        """
        Map an event to an action.
        Triggers the "event mapped" event

        :param controller:              The controller to configure
        :type controller:               steuer.Controller
        """
        if self._configuration_trigger_event.type == pygame.JOYBUTTONDOWN:
            # Map a button event
            controller.mapping['button'][str(self._configuration_mapping_key)] = {"Function": self.action}
        elif self._configuration_trigger_event.type == pygame.JOYAXISMOTION:
            # Map a axis event
            controller.mapping['axis'][str(self._configuration_mapping_key)] = {"Function": self.action}
        elif self._configuration_trigger_event.type == pygame.JOYHATMOTION:
            # Map a hat event
            controller.mapping['hat'][str(self._configuration_mapping_key)] = {"Function": self.action}

        # trigger the "event mapped" event
        if Action.on_event_mapped is not None and _flags['use_events']:
            Action.on_event_mapped(controller, self)


# class that represents a direction. A direction could be a 1:1 mapping to a action
# or it is a result of pressed actions. For example topleft is the combination of top and left
# =====================================================================
class Direction(object):
    def __init__(self, action, value, long_name, short_name, on_heading=None, on_unheading=None):
        """
        Constructor. Creates a direction and save it in Action.directions

        :param action:                  The name of the action that add its value to the direction bitmap
        :type action:                   string
        :param value:                   The value the action adds to the direction bitmap
                                        1: Top
                                        2: Down
                                        4: Left
                                        8: Right
        :type value:                    int
        :param long_name:               The long name of the direction
        :type long_name:                string
        :param short_name:              The short name of the direction
        :type short_name:               string
        :param on_heading:              The callback function that is called when the controller is heading in the direction
        :type on_heading:               function
        :param on_unheading:            The callback function that is called when the controller is unheading in the direction
        :type on_unheading:             function
        """
        # @formatter: off
        self.action = action                # The action that add its value to the direction bitmap
        self.value = value                  # The value the action adds to the direction bitmap
        self.long_name = long_name          # The long name of the direction
        self.short_name = short_name        # The short name of the direction
        self.on_heading = on_heading        # The callback function that is called when the controller is heading in the direction
        self.on_unheading = on_unheading    # The callback function that is called when the controller is unheading in the direction
        # @formatter: on

        Action.directions[str(value)] = self
