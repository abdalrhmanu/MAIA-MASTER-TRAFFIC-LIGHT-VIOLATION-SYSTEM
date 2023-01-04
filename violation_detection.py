import pygame
from enums import VIOLATIONS, COLORS
from screen_settings import set_screen_size

screen, screenWidth, screenHeight, screenSize = set_screen_size()

class ViolationDetection():
    '''This class is used to detect and alert for both vehicles and pedestrians violations.
       Current implementation supports displaying both image and text messages as a violation alert. It receives the vehicle class and uses it to decide whether 
       it refers to a pedestrian or any type of vehicle.'''
    def __init__(self, vehicleClass):
        '''Handles all violation types detection.

        Args:
         - vehicleClass: `str` for indicating the type of object that made the violation.
        '''
        self.violationMessages = {i.name: i.value for i in VIOLATIONS}
        self.vehicleClass = vehicleClass
        self.violationType = self.vehicleClass in ['pedestrian1', 'pedestrian2']
        self.violationText = self.violationMessages['PEDESTRIAN'] if vehicleClass in ['pedestrian1', 'pedestrian2'] else self.violationMessages['CAR']
        self.dimensions = (1000, 50)
        self.font = pygame.font.Font(None, 30)  
    
    def text_objects(self, text, font):
        '''Function used to create a pygame text object.

        Args:
         - text: `str` for the text to be displayed
         - font: `pygame SysFont` for the font type

        Returns: `tuple` consists of both the surface and rectangle generated.
        '''
        textSurface = font.render(text, True, COLORS.RED.value)
        textRect = textSurface.get_rect()
        return textSurface, textRect

    def displayViolation(self):
        '''Displays a text violation on the screen.
        '''
        smallText = pygame.font.SysFont('Arial',20)  # Typo: Sysfont -> SysFont
        textSurf, textRect = self.text_objects(self.violationText, smallText)
        textRect.center = self.dimensions
        screen.blit(textSurf, textRect)
        # time.sleep(2)

    def displayViolationImage(self):
        '''Displays a image violation on the screen.
        '''
        match self.vehicleClass:
            case "motorbike":
                imp = pygame.image.load("images\VIOLATION_MOTORBIKE.png").convert()
            case "car":
                imp = pygame.image.load("images\VIOLATION_CAR.png").convert()
            case _:
                imp = pygame.image.load("images\VIOLATION_PEDESTRIAN.png").convert()

        imp = pygame.transform.scale(imp, (350, 120))
        # imp = pygame.image.load("images\VIOLATION_CAR.png").convert()
        screen.blit(imp, self.dimensions)
        pygame.display.flip()