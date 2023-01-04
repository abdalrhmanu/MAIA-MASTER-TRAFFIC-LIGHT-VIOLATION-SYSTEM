
def get_defaults_colors():
    """
    Default timer values for signals
    """
    timerGreen = {0:10, 1:10, 2:10, 3:10}
    timerRed = 150
    timerYellow = 5
    return timerGreen, timerRed, timerYellow

def get_signal_settings(): 
    """
    Initialization of traffic lights' settings.
    """   
    signalsList = []
    numOfSignals = 4
    nowGreen = 0   # Indicates which traffic light is green currently
    nextGreen = (nowGreen+1)%numOfSignals  #  Indicates which traffic light will turn green next
    nowYellow = 0   # Indicates if the yellow traffic light is on or off

    return signalsList, numOfSignals, nowGreen, nextGreen, nowYellow
    

class TrafficSignal:
    '''This class is used to create a traffic signal object. It contains three attributes representing the different colors of traffic light.
    '''
    def __init__(self, red, yellow, green):
        self.red = red
        self.yellow = yellow
        self.green = green
