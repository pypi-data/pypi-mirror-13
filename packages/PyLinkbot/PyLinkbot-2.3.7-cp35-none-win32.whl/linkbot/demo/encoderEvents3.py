#!/usr/bin/env python3

import linkbot
import time
import sys

def callback(jointNo, angle, timestamp):
    print("Joint ", jointNo, "at angle", angle)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print ("Usage: {0} <Linkbot Serial ID>".format(sys.argv[0]))
        quit()
    serialID = sys.argv[1]
    myLinkbot = linkbot.Linkbot(serialID)
    myLinkbot.enableEncoderEvents(granularity=1.0, cb=callback)
    myLinkbot.drive(90, 90, 90)
    myLinkbot.drive(-90, -90, -90)
    myLinkbot.disableEncoderEvents()

