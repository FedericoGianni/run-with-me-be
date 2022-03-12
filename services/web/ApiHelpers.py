from logging import log

MAX_PARTICIPANTS_VALUE = 200

# HELPERS

def checkLong(long: float):
    if(long <= 180 and long >= -180):
        return True;
    return False;

def checkLat(lat: float):
    if(lat <= 90 and lat >= -90):
        return True;
    return False;

def checkId(id: int):
    if(id == None):
        return False;
    if(int(id) < 0):
        return False;
    return True;

# TODO don't need since difficulty level is calculated inside backend
def checkDifficultyLevel(lvl: float):
    if(lvl < 0.0 or lvl > 5.0):
        return False;
    return True;

def checkTimeStamp(timestamp: int):
    #TODO ?
    return True;

def checkAvgDuration(duration: int):
    # TODO
    return True;

def checkEventName(event_name: str):
    #TODO
    return True;

def checkAvgLength(length: int):
    # TODO
    return True;

def checkAvgPaceMin(min: int):
    # TODO
    return True;

def checkAvgPaceSec(sec : int):
    # TODO
    return True;

def checkAvgPace(min: int, sec:int):
    if(checkAvgPaceMin(min) and checkAvgPaceSec(sec)):
        return True;
    return False;

def decimalToMinutes(distance, duration):

    d = {"minutes_per_km": 0, "seconds_remainder": 0}
    total_seconds = duration*60
    seconds_per_km = float(total_seconds) / float(distance)

    d['minutes_per_km'] = int(seconds_per_km / 60)
    d['seconds_remainder'] = int(seconds_per_km - (d['minutes_per_km'] * 60))

    return d

def calculateAvgPace(distance, duration):
    pace = decimalToMinutes(distance, duration)
    return pace

def calculateDifficultyLevel(distance, duration):
    #calculate a difficulty level in the scale 0 - 5
    level = 0.0

    #need to convert decimal to time
    pace = decimalToMinutes(distance, duration)
    min_per_km = pace.get("minutes_per_km")
    sec_per_km = pace.get("seconds_remainder")

    # 0-3 points assigned for pace
    if(min_per_km <= 4):
        if(sec_per_km <= 30):
            level += 3
        elif(sec_per_km <= 45):
            level += 2.75
        else:
            level += 2.5

    elif(min_per_km <= 5):
        if(sec_per_km <= 15):
            level += 2.25
        elif(sec_per_km <= 30):
            level += 2
        elif(sec_per_km <= 45):
            level += 1.75
        else:
            level += 1.5;
    
    elif(min_per_km <= 6):
        if(sec_per_km <= 30):
            level += 1.25
        elif(sec_per_km <= 45):
            level += 1
        else:
            level += 0.5

    # 0-2 point assigned for distance
    if(distance >= 30):
        level += 2
    elif(distance >= 20):
        level += 1.75
    elif(distance >= 15):
        level += 1.5
    elif(distance >= 10):
        level += 1.25
    elif(distance >= 7.5):
        return 1
    elif(distance >= 5):
        level += 0.75
    elif(distance >= 2.5):
        level += 0.5
    elif(distance >= 1):
        level += 0.25

    return level

def checkMaxParticipants(max: int):
    if(max > MAX_PARTICIPANTS_VALUE):
        return False
    return True

def checkName(name: str):
    # TODO
    return True

def checkUsername(name: str):
    # TODO
    return True

def checkHeight(height: int):
    # TODO
    return True

def checkAge(age: int):
    # TODO
    return True

def checkSex(sex: int):
    # TODO
    return True

def checkFitnessLevel(lvl: float):
    # TODO
    return True

def checkCity(city: str):
    # TODO
    return True

def checkEmail(email: str):
    # TODO
    return True

    