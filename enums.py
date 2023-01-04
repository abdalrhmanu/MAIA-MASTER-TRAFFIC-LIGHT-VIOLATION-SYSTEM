from enum import Enum

class OBJECTS_SPEEDS(Enum):
    car     = 3.0
    motorbike    = 3.1
    pedestrian1 = 2.0
    pedestrian2 = 2.25


class DIRECTIONS(Enum):
    UP      = 'up'
    RIGHT   = 'right'
    BOTTOM  = 'left'
    LEFT    = 'left'

class VIOLATIONS(Enum):
    PEDESTRIAN  = "A violation by a pedestrian."
    CAR         = "A violation by a car or motorbike."

class COLORS(Enum):
    BLACK   = (0, 0, 0)
    WHITE   = (255, 255, 255)
    GREEN   = '#00FF00'
    RED     = '#FF0000'
    GRAY    = '#808080'  
    HOVER   = '#666666'

