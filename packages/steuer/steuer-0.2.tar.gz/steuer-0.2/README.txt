# “Steuer” (english: wheel like “at the wheel”)  
---------------------------------------------
A python module that do a mapping from pygame controller events to actions. Actions are also combined to Directions.

## Feature:

- Configuration of pygame event to module action mappings
  - The configuration will happen for all connected controllers
  - Already mapped controllers are detected and will be mapped automatically
  - The mappings are stored in a mapping database
- Mapping of Events to the configured actions
  - Events set a bitfields that coudl be used to poll for specific actions
  - Events could trigger action and direction callback functions
  - Events could trigger action callback functions
  - Events could set the action mapped to the event. This action could be processed without calling a Steuer callback automatically

## Prerequisites: 
- pygame

## contact: 
-----------
thorsten.butschke@googlemail.com