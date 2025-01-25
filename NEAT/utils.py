import colorsys
import math

def positive_angle(angle):
    '''Converts an angle in degrees to its positive identity.'''
    return angle if angle >= 0 else 360 + angle

def hsv2rgb(h, s, v):
    '''Convert HSV to RGB'''
    return tuple(round(i * 255) for i in colorsys.hsv_to_rgb(h, s, v))

def distance(x1, y1, x2, y2):
    '''Calculate the Euclidean distance between two points'''
    return math.sqrt((x1 - x2)**2 + (y1 - y2)**2)
