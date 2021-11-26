# HELPERS

def checkLong(long: float):
    if(long <= 180 and long >= -180):
        return True;
    return False;

def checkLat(lat: float):
    if(lat <= 90 and lat >= -90):
        return True;
    return False;

def checkDifficultyLevel(lvl: float):
    if(difficulty_level < 0.0 or difficulty_level > 5.0):
        return False;
    return True;