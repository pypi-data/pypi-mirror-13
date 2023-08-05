#!/usr/bin/env python3

import linkbot

def callback(*args):
    print("Button event.")

l = linkbot.Linkbot()
l.enable_button_events(callback)
input("Press 'Enter' to quit.")
