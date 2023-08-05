#!/usr/bin/env python3

import linkbot
import math
import time
import random

'''
linkbotIds = [ '4NKJ', 'X3XH', '5J66', '4LB8',
               'CJTX', 'WVF2', '6SSJ', 'DWRJ',
               'NJ3Q', 'FJ6C' ,'XQKJ', '2XWX']
'''
linkbotIds = ['locl']

linkbots = list(map(linkbot.Linkbot, linkbotIds))

t = 0.0
while True:
    print("Loop")
    r = (math.sin(t)+1)*127.0
    g = (math.sin(t+2*math.pi/3)+1)*127.0
    b = (math.sin(t+4*math.pi/3)+1)*127.0
    '''
    r = random.randint(1, 255)
    g = random.randint(1, 255)
    b = random.randint(1, 255)
    '''

    for linkbot in linkbots:
        linkbot.setLedColor(int(r), int(g), int(b))

    t += 0.1
