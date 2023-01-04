import pygame

def set_screen_size():
    # Screensize
    screenWidth = 1400
    screenHeight = 900
    screenSize = (screenWidth, screenHeight)
    displayScreen = pygame.display.set_mode(screenSize)

    return displayScreen, screenWidth, screenHeight, screenSize

def blit_screen(displayScreen, source, pos):
    displayScreen.blit(source, pos)

def set_screen_objects():
    # Setting background image i.e. image of intersection
    backgroundImage = pygame.image.load('images/background.png')

    # Set the size for the image
    DEFAULT_IMAGE_SIZE = (1400, 922)
    DEFAULT_SIGNAL_SIZE = (32, 98)
    PEDESTRIAN_SIGNAL_SIZE_0 = (25,65)
    PEDESTRIAN_SIGNAL_SIZE_90 = (65,25)

    # Scale the image to your needed size
    backgroundImage = pygame.transform.scale(backgroundImage, DEFAULT_IMAGE_SIZE)

    pygame.display.set_caption("Traffic Simulation Project")

    # Loading signal images and font
    redLight = pygame.image.load('images/signals/red.png')
    redLight = pygame.transform.scale(redLight, DEFAULT_SIGNAL_SIZE)

    yellowLight = pygame.image.load('images/signals/yellow.png')
    yellowLight = pygame.transform.scale(yellowLight, DEFAULT_SIGNAL_SIZE)

    greenLight = pygame.image.load('images/signals/green.png')
    greenLight = pygame.transform.scale(greenLight, DEFAULT_SIGNAL_SIZE)

    redLightPed = pygame.image.load('images/signals/pedestrians_red_0.png')
    redLightPed = pygame.transform.scale(redLightPed, PEDESTRIAN_SIGNAL_SIZE_0)

    redLightPed270 = pygame.image.load('images/signals/pedestrians_red_270.png')
    redLightPed270 = pygame.transform.scale(redLightPed270, PEDESTRIAN_SIGNAL_SIZE_90)

    redLightPed180 = pygame.image.load('images/signals/pedestrians_red_180.png')
    redLightPed180 = pygame.transform.scale(redLightPed180, PEDESTRIAN_SIGNAL_SIZE_0)

    redLightPed90 = pygame.image.load('images/signals/pedestrians_red_90.png')
    redLightPed90 = pygame.transform.scale(redLightPed90, PEDESTRIAN_SIGNAL_SIZE_90)

    greenLightPed = pygame.image.load('images/signals/pedestrians_green_0.png')
    greenLightPed = pygame.transform.scale(greenLightPed, PEDESTRIAN_SIGNAL_SIZE_0)

    greenLightPed270= pygame.image.load('images/signals/pedestrians_green_270.png')
    greenLightPed270 = pygame.transform.scale(greenLightPed270, PEDESTRIAN_SIGNAL_SIZE_90)

    greenLightPed180= pygame.image.load('images/signals/pedestrians_green_180.png')
    greenLightPed180 = pygame.transform.scale(greenLightPed180, PEDESTRIAN_SIGNAL_SIZE_0)

    greenLightPed90= pygame.image.load('images/signals/pedestrians_green_90.png')
    greenLightPed90 = pygame.transform.scale(greenLightPed90, PEDESTRIAN_SIGNAL_SIZE_90)


    font = pygame.font.Font(None, 30)

    return backgroundImage, greenLightPed, greenLightPed90, greenLightPed180, greenLightPed270 , \
    redLight, yellowLight, greenLight, redLightPed, redLightPed180, redLightPed90, \
    redLightPed270 ,font