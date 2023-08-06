# Script Name		: timer.py
# Author			: Tony Hammack
# Created			: 23 December 2015
# Last Modified		: 22 February 2016
# Version			: 1

# Classes imported
import datetime
import time


class Timer(object):


    def __init__(self):
        pass


    def start(self):
        """Starts the timer"""
        dt = datetime.datetime.now()
        self.start = dt.timetuple()
        return time.mktime(self.start)


    def stop(self):
        """Stops the timer.  Returns the time elapsed"""
        dt = datetime.datetime.now()
        self.start = dt.timetuple()
        return time.mktime(self.start)