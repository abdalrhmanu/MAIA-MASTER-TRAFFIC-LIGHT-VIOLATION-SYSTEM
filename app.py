import os
# Next line just to stop showing Pygame welcoming message on every run.
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

import random
import time
import threading
import pygame
import sys

from loguru import logger
from enums import OBJECTS_SPEEDS, VIOLATIONS, COLORS


# Imports
from violation_detection import ViolationDetection
from screen_settings import set_screen_size, blit_screen, set_screen_objects
from traffic_signal import get_defaults_colors, get_signal_settings, TrafficSignal

# Flag cars
SIMULATION_VIOLATION = False

VIOLATION = None

SLEEP_TIME_5 = 5
SLEEP_TIME_1 = 1


speeds = {i.name: i.value for i in OBJECTS_SPEEDS}  

timerGreen, timerRed, timerYellow = get_defaults_colors()
signalsList, numOfSignals, nowGreen, nextGreen, nowYellow = get_signal_settings()

# Pygame screen settings
displayScreen, screenWidth, screenHeight, screenSize = set_screen_size()

# Coordinates of vehicles' and pedestrians' start
x = {'right':[0,0,0], 'down':[765,737,697], 'left':[1400,1400,1400], 'up':[602,627,657]}    
y = {'right':[348,370,398], 'down':[0,0,0], 'left':[548,506,456], 'up':[800,800,800]}
x_ped = {'right':[0,0,0], 'down':[870,900,930], 'left':[1400,1400,1400],'up':[430,460,490]}
y_ped = {'right':[190,220,250], 'down':[0,0,0], 'left':[630,660,690],'up':[900,900,900]}

roadObj = {'right': {0:[], 1:[], 2:[], 'crossed':0}, 'down': {0:[], 1:[], 2:[], 'crossed':0}, 'left': {0:[], 1:[], 2:[], 'crossed':0}, 'up': {0:[], 1:[], 2:[], 'crossed':0}}
roadObjTypes = {1:'car', 2:'motorbike',3:'pedestrian1',4:'pedestrian2'}
directionsNum = {0:'right', 1:'down', 2:'left', 3:'up'}

# Coordinates of traffic lights' positions
lightCoords = [(530,230),(810,230),(810,570),(530,570)]
lightPedCoords = [(460,230),(850,230),(900,610),(480,680)]

# Coordinates of vehicles' and pedestrians' stop lines 
stopCoords = {'right': 430, 'down': 220, 'left': 990, 'up': 710}
stopCoordsPed = {'right': 510, 'down': 330, 'left': 840, 'up': 610}
defaultStopCoords = {'right': 430, 'down': 210, 'left': 1000, 'up': 720}
defaultStopPed = {'right': 500, 'down': 330, 'left': 850, 'up': 600}

# Gap between vehicles
positionGap = 25    # stopping gap

# Parameters for turning vehicles:
roadObjTurned = {'right': {0:[], 1:[], 2:[]}, 'down': {0:[], 1:[], 2:[]}, 'left': {0:[], 1:[], 2:[]}, 'up': {0:[], 1:[], 2:[]}}
roadObjNotTurned = {'right': {0:[], 1:[], 2:[]}, 'down': {0:[], 1:[], 2:[]}, 'left': {0:[], 1:[], 2:[]}, 'up': {0:[], 1:[], 2:[]}}
angleRotation = 3 
midCoords = {'right': {'x':705, 'y':445}, 'down': {'x':695, 'y':450}, 'left': {'x':695, 'y':425}, 'up': {'x':695, 'y':400}} #represents the coordinates of the middle point of the road intersectioin, from where vehicles would turn

pygame.init()
simulation = pygame.sprite.Group()

class RoadObjects(pygame.sprite.Sprite):
    """
    This class contains all the attributes and methods that correspond to road objects (cars, motorbikes and pedestrians).
    It defines all the parameters of the road objects, such as size, lane, direction, speed and whether they will turn or not.
    It controls all their movements, and determines when they can cross the intersection according to the traffic lights' logic.

    """
    def __init__(self, laneNum, roadObjClass, directionNumber, direction, willTurn):
        pygame.sprite.Sprite.__init__(self)
        self.laneNum = laneNum
        self.roadObjClass = roadObjClass
        self.speed = speeds[roadObjClass]
        self.directionNumber = directionNumber
        self.direction = direction
        if (self.roadObjClass == 'pedestrian1') or (self.roadObjClass == 'pedestrian2'):
            self.x = x_ped[direction][laneNum]
        else:
            self.x = x[direction][laneNum]
        if (self.roadObjClass == 'pedestrian1') or (self.roadObjClass == 'pedestrian2'):
            self.y = y_ped[direction][laneNum]
        else:
            self.y = y[direction][laneNum]
        self.crossed = random.randint(0,1)
        # self.crossed = 0 #I commented the random version of this line to see if it works without the violations, then change it back
        self.willTurn = willTurn 
        self.turned = 0 
        self.rotationAngle = 0 
        roadObj[direction][laneNum].append(self)
        self.objIndex = len(roadObj[direction][laneNum]) - 1
        self.crossedObjIndex = 0
        imagePath = "images/" + direction + "/" + roadObjClass + ".png"
        self.originalImage = pygame.image.load(imagePath)
        self.image = pygame.image.load(imagePath)

        if self.roadObjClass not in ['pedestrian1', 'pedestrian2']:
            if(direction == 'up' or direction == 'down'):
                dim = (33, 80)
            else:
                dim = (80, 33)
            self.originalImage = pygame.transform.scale(self.originalImage,dim)
            self.image = pygame.transform.scale(self.image, dim)
        else:
            self.image = pygame.transform.scale(self.image, (25,25))

        if self.crossed == 1:
            global SIMULATION_VIOLATION
            global VIOLATION 
            
            VIOLATION = ViolationDetection(vehicleClass = self.roadObjClass)
            SIMULATION_VIOLATION = not SIMULATION_VIOLATION
        else:
            SIMULATION_VIOLATION = False

        if(len(roadObj[direction][laneNum])>1 and roadObj[direction][laneNum][self.objIndex-1].crossed==0):    # if more than 1 vehicle in the lane of vehicle before it has crossed stop line
            if(direction=='right'):
                self.stop = roadObj[direction][laneNum][self.objIndex-1].stop - roadObj[direction][laneNum][self.objIndex-1].image.get_rect().width - positionGap         # setting stop coordinate as: stop coordinate of next vehicle - width of next vehicle - gap
            elif(direction=='left'):
                self.stop = roadObj[direction][laneNum][self.objIndex-1].stop + roadObj[direction][laneNum][self.objIndex-1].image.get_rect().width + positionGap
            elif(direction=='down'):
                self.stop = roadObj[direction][laneNum][self.objIndex-1].stop - roadObj[direction][laneNum][self.objIndex-1].image.get_rect().height - positionGap
            elif(direction=='up'):
                self.stop = roadObj[direction][laneNum][self.objIndex-1].stop + roadObj[direction][laneNum][self.objIndex-1].image.get_rect().height + positionGap
        else:
            self.stop = defaultStopCoords[direction]

        if (self.roadObjClass == 'pedestrian1') or (self.roadObjClass == 'pedestrian2'):
            self.stop = defaultStopPed[direction]
        else:
            self.stop = defaultStopCoords[direction]

        # Set new starting and stopping coordinate
        if(direction=='right'):
            temp = self.image.get_rect().width + positionGap
            x[direction][laneNum] -= temp
        elif(direction=='left'):
            temp = self.image.get_rect().width + positionGap
            x[direction][laneNum] += temp
        elif(direction=='down'):
            temp = self.image.get_rect().height + positionGap
            y[direction][laneNum] -= temp
        elif(direction=='up'):
            temp = self.image.get_rect().height + positionGap
            y[direction][laneNum] += temp
        simulation.add(self)

    def updateRotationAngles(self):
        """
        This function is used to update the angle of rotation of the road object
        """
        self.rotationAngle += angleRotation

        if(self.rotationAngle==90):
                                self.turned = 1
                                roadObjTurned[self.direction][self.laneNum].append(self)
                                self.crossedObjIndex = len(roadObjTurned[self.direction][self.laneNum]) - 1

        return pygame.transform.rotate(self.originalImage, self.rotationAngle)
        

    def controlMovement(self):
        """
        This function controls the movements of all road objects (cars, motorbikes and pedestrians).
        """
        if(self.direction=='right'):
            if (self.roadObjClass == 'pedestrian1') or (self.roadObjClass == 'pedestrian2'):
                """
                Control of the movement and crossing of pedestrians going from left to right
                """
                if(self.crossed==0 and self.x+self.image.get_rect().width>stopCoordsPed[self.direction]):   # if the pedestrian has crossed the stopline 
                    self.crossed = 1
                if((self.x+self.image.get_rect().width<=self.stop or self.crossed==1 or (nowGreen==2 and nowYellow==0)) and (self.objIndex==0 or self.x+self.image.get_rect().width<(roadObj[self.direction][self.laneNum][self.objIndex-1].x - positionGap))):
                # (if the pedestrian has not reached the stop coordinate, or has crossed the stopline, or has a green traffic light) and (it is the first pedestrian in that lane or it has enough gap to the next pedestrian in the same lane)
                    self.x += self.speed  # move the pedestrian
            else:
                """
                Control of the movement of cars and motorbikes going from left to right
                """
                if(self.crossed==0 and self.x+self.image.get_rect().width>stopCoords[self.direction]): # if the road object has crossed the stopline 
                    self.crossed = 1
                    roadObj[self.direction]['crossed'] += 1
                    if(self.willTurn==0): # if the vehicle will not turn
                        roadObjNotTurned[self.direction][self.laneNum].append(self)
                        self.crossedObjIndex = len(roadObjNotTurned[self.direction][self.laneNum]) - 1
                if(self.willTurn==1): # if the vehicle will turn
                    if(self.crossed==0 or self.x+self.image.get_rect().width<stopCoords[self.direction]+200):
                        if((self.x+self.image.get_rect().width<=self.stop or (nowGreen==0 and nowYellow==0) or self.crossed==1) and (self.objIndex==0 or self.x+self.image.get_rect().width<(roadObj[self.direction][self.laneNum][self.objIndex-1].x - positionGap) or roadObj[self.direction][self.laneNum][self.objIndex-1].turned==1)):  
                        # (if the road object has not reached the stop coordinate, or has a green traffic light, or has crossed the stopline) and (it is the first object in that lane or it has enough gap to the next vehicle in the same lane, also if the vehicle ahead has already turned, then overlap is no longer an issue)             
                            self.x += self.speed
                    else:
                        if(self.turned==0):
                            """
                            Once the vehicle crosses the turning point, if the turned value is 0, it turns as it rotates alongthe x and y axes. Once the angle of rotations is 90 degrees, the turned variable is set to 1, the vehicle is added to the vehiclesTurned list, and its crossedObjIndex is updated.
                            """
                            self.image = self.updateRotationAngles()
                            self.x += 2.4
                            self.y -= 2.8
                        else:
                            """
                            Else, if the turned value is 1, the vehicle moves only if there is enough gap from the vehicle ahead. The decision is based on the same conditions as previous case.
                            """
                            if(self.crossedObjIndex==0 or (self.y>(roadObjTurned[self.direction][self.laneNum][self.crossedObjIndex-1].y + roadObjTurned[self.direction][self.laneNum][self.crossedObjIndex-1].image.get_rect().height + positionGap))):
                                self.y -= self.speed
                else: #in case the vehicle will not turn:
                    if(self.crossed == 0):
                        if((self.x+self.image.get_rect().width<=self.stop or (nowGreen==0 and nowYellow==0)) and (self.objIndex==0 or self.x+self.image.get_rect().width<(roadObj[self.direction][self.laneNum][self.objIndex-1].x - positionGap))):                
                            self.x += self.speed
                    else:
                        if((self.crossedObjIndex==0) or (self.x+self.image.get_rect().width<(roadObjNotTurned[self.direction][self.laneNum][self.crossedObjIndex-1].x - positionGap))):                 
                            self.x += self.speed
        elif(self.direction=='down'):
            if (self.roadObjClass == 'pedestrian1') or (self.roadObjClass == 'pedestrian2'):
                """
                Control of the movement and crossing of pedestrians going from the top to the bottom of the screen.
                The logic is the same as the one used in the previous case.
                """
                if(self.crossed==0 and self.y+self.image.get_rect().height>stopCoordsPed[self.direction]):
                    self.crossed = 1
                if((self.y+self.image.get_rect().height<=self.stop or self.crossed == 1 or (nowGreen==3 and nowYellow==0)) and (self.objIndex==0 or self.y+self.image.get_rect().height<(roadObj[self.direction][self.laneNum][self.objIndex-1].y - positionGap))):
                    self.y += self.speed
            else:
                """
                Control of the movement and crossing of cars and motorbikes going from the top to the bottom of the screen.
                The logic is the same as the one used in the previous case.
                """
                if(self.crossed==0 and self.y+self.image.get_rect().height>stopCoords[self.direction]):
                    self.crossed = 1
                    roadObj[self.direction]['crossed'] += 1
                    if(self.willTurn==0):
                        roadObjNotTurned[self.direction][self.laneNum].append(self)
                        self.crossedObjIndex = len(roadObjNotTurned[self.direction][self.laneNum]) - 1
                if(self.willTurn==1):
                    if(self.crossed==0 or self.y+self.image.get_rect().height<stopCoords[self.direction]+200):
                        if((self.y+self.image.get_rect().height<=self.stop or (nowGreen==1 and nowYellow==0) or self.crossed==1) and (self.objIndex==0 or self.y+self.image.get_rect().height<(roadObj[self.direction][self.laneNum][self.objIndex-1].y - positionGap) or roadObj[self.direction][self.laneNum][self.objIndex-1].turned==1)):                
                            self.y += self.speed
                    else:   
                        if(self.turned==0):
                            self.image = self.updateRotationAngles()
                            self.x += 1.2
                            self.y += 1.8
                        else:
                            if(self.crossedObjIndex==0 or ((self.x + self.image.get_rect().width) < (roadObjTurned[self.direction][self.laneNum][self.crossedObjIndex-1].x - positionGap))):
                                self.x += self.speed
                else: 
                    if(self.crossed == 0):
                        if((self.y+self.image.get_rect().height<=self.stop or (nowGreen==1 and nowYellow==0)) and (self.objIndex==0 or self.y+self.image.get_rect().height<(roadObj[self.direction][self.laneNum][self.objIndex-1].y - positionGap))):                
                            self.y += self.speed
                    else:
                        if((self.crossedObjIndex==0) or (self.y+self.image.get_rect().height<(roadObjNotTurned[self.direction][self.laneNum][self.crossedObjIndex-1].y - positionGap))):                
                            self.y += self.speed


        elif(self.direction=='left'):
            if (self.roadObjClass == 'pedestrian1') or (self.roadObjClass == 'pedestrian2'):
                """
                Control of the movement and crossing of pedestrians going from right to left.
                The logic is the same as the one used in the previous cases.
                """
                if(self.crossed==0 and self.x<stopCoordsPed[self.direction]):
                    self.crossed = 1
                if((self.x>=self.stop or self.crossed == 1 or (nowGreen==0 and nowYellow==0)) and (self.objIndex==0 or self.x>(roadObj[self.direction][self.laneNum][self.objIndex-1].x + roadObj[self.direction][self.laneNum][self.objIndex-1].image.get_rect().width + positionGap))):
                    self.x -= self.speed
            else:
                """
                Control of the movement and crossing of cars and motorbikes going from the right to the left.
                The logic is the same as the one used in the previous cases.
                """
                if(self.crossed==0 and self.x<stopCoords[self.direction]):
                    self.crossed = 1
                    roadObj[self.direction]['crossed'] += 1
                    if(self.willTurn==0):
                        roadObjNotTurned[self.direction][self.laneNum].append(self)
                        self.crossedObjIndex = len(roadObjNotTurned[self.direction][self.laneNum]) - 1
                if(self.willTurn==1):
                    if(self.crossed==0 or self.x>stopCoords[self.direction]-200):
                        if((self.x>=self.stop or (nowGreen==2 and nowYellow==0) or self.crossed==1) and (self.objIndex==0 or self.x>(roadObj[self.direction][self.laneNum][self.objIndex-1].x + roadObj[self.direction][self.laneNum][self.objIndex-1].image.get_rect().width + positionGap) or roadObj[self.direction][self.laneNum][self.objIndex-1].turned==1)):                
                            self.x -= self.speed
                    else: 
                        if(self.turned==0):
                            self.image = self.updateRotationAngles()
                            self.x -= 1
                            self.y += 1.2
                        else:
                            if(self.crossedObjIndex==0 or ((self.y + self.image.get_rect().height) <(roadObjTurned[self.direction][self.laneNum][self.crossedObjIndex-1].y  -  positionGap))):
                                self.y += self.speed
                else: 
                    if(self.crossed == 0):
                        if((self.x>=self.stop or (nowGreen==2 and nowYellow==0)) and (self.objIndex==0 or self.x>(roadObj[self.direction][self.laneNum][self.objIndex-1].x + roadObj[self.direction][self.laneNum][self.objIndex-1].image.get_rect().width + positionGap))):                
                            self.x -= self.speed
                    else:
                        if((self.crossedObjIndex==0) or (self.x>(roadObjNotTurned[self.direction][self.laneNum][self.crossedObjIndex-1].x + roadObjNotTurned[self.direction][self.laneNum][self.crossedObjIndex-1].image.get_rect().width + positionGap))):                
                            self.x -= self.speed
                            if(self.crossed==0 and self.x<stopCoords[self.direction]):
                                self.crossed = 1
                            if((self.x>=self.stop or self.crossed == 1 or (nowGreen==2 and nowYellow==0)) and (self.objIndex==0 or self.x>(roadObj[self.direction][self.laneNum][self.objIndex-1].x + roadObj[self.direction][self.laneNum][self.objIndex-1].image.get_rect().width + positionGap))):
                                self.x -= self.speed
        elif(self.direction=='up'):
            if (self.roadObjClass == 'pedestrian1') or (self.roadObjClass == 'pedestrian2'):
                """
                Control of the movement and crossing of pedestrians going from the bottom to the top of the screen.
                The logic is the same as the one used in the previous case.
                """
                if(self.crossed==0 and self.y<stopCoordsPed[self.direction]):
                    self.crossed = 1
                    #print("PEDESTRIAN ALLOWED TO CROSS UP, ALREADY CROSSED STOPLINE")
                if((self.y>=self.stop or self.crossed == 1 or (nowGreen==1 and nowYellow==0)) and (self.objIndex==0 or self.y>(roadObj[self.direction][self.laneNum][self.objIndex-1].y + roadObj[self.direction][self.laneNum][self.objIndex-1].image.get_rect().height + positionGap))):
                    self.y -= self.speed
                    #print("PEDESTRIAN ALLOWED TO CROSS UP")
            else:
                """
                Control of the movement and crossing of cars and motorbikes going from the bottom to the top of the screen.
                The logic is the same as the one used in the previous cases.
                """
                if(self.crossed==0 and self.y<stopCoords[self.direction]):
                    self.crossed = 1
                    roadObj[self.direction]['crossed'] += 1
                    if(self.willTurn==0):
                        roadObjNotTurned[self.direction][self.laneNum].append(self)
                        self.crossedObjIndex = len(roadObjNotTurned[self.direction][self.laneNum]) - 1
                if(self.willTurn==1):
                    if(self.crossed==0 or self.y>stopCoords[self.direction]-170):
                        if((self.y>=self.stop or (nowGreen==3 and nowYellow==0) or self.crossed == 1) and (self.objIndex==0 or self.y>(roadObj[self.direction][self.laneNum][self.objIndex-1].y + roadObj[self.direction][self.laneNum][self.objIndex-1].image.get_rect().height +  positionGap) or roadObj[self.direction][self.laneNum][self.objIndex-1].turned==1)):
                            self.y -= self.speed
                    else:   
                        if(self.turned==0):
                            self.image = self.updateRotationAngles()
                            self.x -= 2
                            self.y -= 1.2
                            
                        else:
                            if(self.crossedObjIndex==0 or (self.x>(roadObjTurned[self.direction][self.laneNum][self.crossedObjIndex-1].x + roadObjTurned[self.direction][self.laneNum][self.crossedObjIndex-1].image.get_rect().width + positionGap))):
                                self.x -= self.speed
                else: 
                    if(self.crossed == 0):
                        if((self.y>=self.stop or (nowGreen==3 and nowYellow==0)) and (self.objIndex==0 or self.y>(roadObj[self.direction][self.laneNum][self.objIndex-1].y + roadObj[self.direction][self.laneNum][self.objIndex-1].image.get_rect().height + positionGap))):                
                            self.y -= self.speed
                    else:
                        if((self.crossedObjIndex==0) or (self.y>(roadObjNotTurned[self.direction][self.laneNum][self.crossedObjIndex-1].y + roadObjNotTurned[self.direction][self.laneNum][self.crossedObjIndex-1].image.get_rect().height + positionGap))):                
                            self.y -= self.speed 

def initializeTrafficSignal():
    """
    This function initializes four objects of the class TrafficSignal in a clockwise directions, with their respective timers.

    Args:
        -None

    Returns:
        None

    """
    traffic_signal_1 = TrafficSignal(0, timerYellow, timerGreen[0])
    signalsList.append(traffic_signal_1)
    signalsList.append(TrafficSignal(traffic_signal_1.red+traffic_signal_1.yellow+traffic_signal_1.green, timerYellow, timerGreen[1]))
    signalsList.append(TrafficSignal(timerRed, timerYellow, timerGreen[2]))
    signalsList.append(TrafficSignal(timerRed, timerYellow, timerGreen[3]))
    iterateUpdateValues()

def iterateUpdateValues():
    """This function is called repeatedly to control all traffic light visuals.

    Args:
        - None

    Returns: None
    
    """
    global nowGreen, nowYellow, nextGreen
    while(signalsList[nowGreen].green>0):  
        updateValues()
        time.sleep(1)
    nowYellow = 1   
    
    for i in range(0,3):
        for vehicle in roadObj[directionsNum[nowGreen]][i]:
            vehicle.stop = defaultStopCoords[directionsNum[nowGreen]]
    while(signalsList[nowGreen].yellow>0):  
        updateValues()
        time.sleep(2)
    nowYellow = 0   


    signalsList[nowGreen].green = timerGreen[nowGreen]
    signalsList[nowGreen].yellow = timerYellow
    signalsList[nowGreen].red = timerRed

    nowGreen = nextGreen 
    nextGreen = (nowGreen+1)%numOfSignals    
    signalsList[nextGreen].red = signalsList[nowGreen].yellow+signalsList[nowGreen].green 
    iterateUpdateValues()

# Update values of the signal timers after every second
def updateValues():
    for i in range(0, numOfSignals):
        if(i==nowGreen):
            if(nowYellow==0):
                signalsList[i].green-=1
            else:
                signalsList[i].yellow-=1
        else:
            signalsList[i].red-=1

def generateRoadObjects():
    """This function will be called to generate all type of moving road objects, which include any object saved in the
    enum `ObjectTypes`.

    Reference: None

    Args:
     - None

    Returns:
     - A road object (motorbike, car, or pedestrian) randomly generated on different lanes and moving on different directions.
    
    """

    while(True):
        vehicle_type = random.randint(1,len(OBJECTS_SPEEDS))
        willTurn = 0
        temp = random.randint(0,99)
        if temp<40:
            willTurn = 1
        temp = random.randint(0,99)
        lane_n = random.randint(0,1)
        directionNumber = 0
        dist = [25,50,75,100]

        if(temp<dist[0]):
            directionNumber = 0
        elif(temp<dist[1]):
            directionNumber = 1
        elif(temp<dist[2]):
            directionNumber = 2
        elif(temp<dist[3]):
            directionNumber = 3

        RoadObjects(random.randint(1,2) if vehicle_type <= 2 else lane_n, roadObjTypes[vehicle_type], directionNumber, directionsNum[directionNumber],willTurn if vehicle_type <= 2 else 0)
        time.sleep(SLEEP_TIME_1)

class Run:
    """ This class is called to trigger the simulation of traffic light violation detection project. 
    It controls all of the processes and triggers the necessary functions. 
    
    """
    thread1 = threading.Thread(name="initialization",target=initializeTrafficSignal, args=())    
    thread1.daemon = True
    thread1.start()

    backgroundImage, greenLightPed, greenLightPed90, greenLightPed180, greenLightPed270 , \
    redLight, yellowLight, greenLight, redLightPed, redLightPed180, redLightPed90, \
    redLightPed270 ,font = set_screen_objects()

    thread2 = threading.Thread(name="generateRoadObjects",target=generateRoadObjects, args=()) 
    thread2.daemon = True
    thread2.start()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

        blit_screen(displayScreen, backgroundImage,(0,0))   
        for i in range(0,numOfSignals):  
            if(i==nowGreen):
                if(nowYellow==1):
                    blit_screen(displayScreen, yellowLight, lightCoords[i])
                else:
                    blit_screen(displayScreen, greenLight, lightCoords[i])
            else:
                blit_screen(displayScreen, redLight, lightCoords[i])

        if nowGreen == 1:
            blit_screen(displayScreen, greenLightPed, lightPedCoords[0])
        else:
            blit_screen(displayScreen, redLightPed, lightPedCoords[0])

        if nowGreen == 2:
            blit_screen(displayScreen, greenLightPed270, lightPedCoords[1])
        else:
            blit_screen(displayScreen, redLightPed270, lightPedCoords[1])

        if nowGreen == 3:
            blit_screen(displayScreen, greenLightPed180, lightPedCoords[2])
        else:
            blit_screen(displayScreen, redLightPed180, lightPedCoords[2])

        if nowGreen == 0:
            blit_screen(displayScreen, greenLightPed90, lightPedCoords[3])
        else:
            blit_screen(displayScreen, redLightPed90, lightPedCoords[3])

        for vehicle in simulation:
            blit_screen(displayScreen, vehicle.image, [vehicle.x, vehicle.y])
            vehicle.controlMovement()

        if(SIMULATION_VIOLATION):
            VIOLATION.displayViolationImage()

        pygame.display.update()


Run()
