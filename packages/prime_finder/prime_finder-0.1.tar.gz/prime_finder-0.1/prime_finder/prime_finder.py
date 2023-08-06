#!/usr/bin/env python

# Script Name		: prime_finder.py
# Author			: Tony Hammack
# Created			: 23 December 2015
# Last Modified		: 4 February 2016
# Version			: 1.5

# Classes imported
import logging
import os
import sys

from timer import Timer


# Classes created
class InvalidArgumentException(Exception):      # Custom Exception
    pass


# **** Constants ****
LOG_FILE = 'prime_finder.log'      # Log file
MINUTES = 0.5                 # user can define global duration in minutes that algorithm can use


# ***** Functions ***

# Utilities

def clear_screen():
    "# Function to clear the screen"
    if os.name == "posix":  # Unix/Linux/MacOS/BSD/etc
        return os.system('clear')  # Clear the Screen
    elif os.name in ("nt", "dos", "ce"):  # DOS/Windows
        return os.system('CLS')


def new_program():
    # New Program
    clear_screen()
    load_program()


def reload_finder():
    # reloads the program
    response = raw_input("Do you want to restart the prime finder? (yes or no): ")
    if response == "yes":
        new_program()
    elif response == "no":
        clear_screen()
        sys.exit()  # closes form


def load_program( t= Timer):
    # Main Program

    # First Logger
    log_specifics_debug('START', 'Starting the Prime Finder.')

    # initial variable input
    try:
        # User input
        userString = raw_input("Please input an integer: ")
        userNumber = int(userString)
        log_specifics_debug('USER INPUT', 'Input was successful.')

        # Initiates Timer class object
        t = Timer()
        start_time = t.start()

        # Prime Finder
        prime_finder(userNumber, start_time)
        log_specifics_debug('PRIME FINDER', 'prime_finder module completed.')

        # Reload prime finder
        response = raw_input("Do you want to restart the prime finder? (yes or no): ")
        if response == "yes":
            log_specifics_debug('RELOADING', 'Prime Finder is reloading.')
            new_program()
        elif response == "no":
            clear_screen()
            log_specifics_debug('CLOSING', 'Prime Finder is closing.')
            sys.exit()

    except ValueError as err:
        log_specifics_debug('USER INPUT', userString)
        log_specifics_critical('USER INPUT', 'User entered a non-integer literal.')
        # Restarts Prime Finder application
        response = raw_input("Do you want to restart the prime finder? (yes or no): ")
        if response == "yes":
            log_specifics_debug('RELOADING', 'Prime Finder is reloading.')
            new_program()
        elif response == "no":
            clear_screen()
            log_specifics_debug('CLOSING', 'Prime Finder is closing.')
            sys.exit()

    except KeyboardInterrupt as err:
        log_specifics_debug('Closing', 'User has manually closed program.')
        sys.exit()

    except RuntimeError as err:
        log_specifics_debug('RUNTIME ERROR', err)
        # Restarts Prime Finder application
        response = raw_input("Do you want to restart the prime finder? (yes or no): ")
        if response == "yes":
            log_specifics_debug('RELOADING', 'Prime Finder is reloading.')
            new_program()
        elif response == "no":
            log_specifics_debug('CLOSING', 'Prime Finder is closing.')
            clear_screen()
            sys.exit()


# Prime Finder Algorithm
def prime_finder(num, p_start):  # prime factor algorithm
    log_specifics_debug('START TIME', 'Start of algorithm: ' + str(p_start))
    print "Here are your prime factors...."
    mod = 2
    while mod <= num:
        test = compare_time(p_start)
        if test:
            while num % mod == 0:
                num = num / mod
                final_output(mod)  # displays output
            mod += 1  # increases modulus by one
        else:
            print "Time of algorithm exceeded predetermined limit of: " + str(MINUTES) + " minutes."
            break
    log_endoftime(p_start)


def final_output(factors):  # prints modulus out
    log_specifics_debug('FACTORS', factors)
    print factors

# Timer class objects


def start_time():           # Start Time
    t = Timer()
    return t.start()


def stop_time():            # Stop Time
    t = Timer()
    return t.stop()


def difference_time(p_start):           # Difference between start and end times
        stop = stop_time()
        return stop - p_start


def compare_time(p_start):      # Compares Time
    seconds = MINUTES * 60        # User can specify seconds to limit program
    while difference_time(p_start) < seconds:
        return True
    return False

# Loggers


def log_endoftime(p_start):
    log_stop = stop_time()
    log_specifics_debug('END TIME', 'End of algorithm: ' + str(log_stop))
    log_specifics_debug('LENGTH  TIME', 'Time of algorithm: ' + str(log_stop - p_start) + " seconds.")


def log_specifics_debug(section, message):          # Logs debug information with section/message
    log = logging.getLogger(section)
    log.debug(message)


def log_specifics_critical(section, message):       # Logs critical information with section/message
    log = logging.getLogger(section)
    log.critical(message)


def log_specifics_info(section, message):       # Logs critical information with section/message
    log = logging.getLogger(section)
    log.info(message)


def purge_log():
    with open(LOG_FILE, 'w') as file:
            file.truncate()


# *****Ends Functions****

if __name__ == "__main__":
    # set up logging to file
    logging.basicConfig(level=logging.DEBUG,
                      format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                      datefmt='%d-%m-%y %H:%M',              # Date Format
                      filename=LOG_FILE,                  # Name of log
                      filemode='a')                       # Appends log
    # define a Handler which writes INFO messages or higher to the sys.stderr
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    # set a format which is simpler for console use
    formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
    # tell the handler  to use this format
    console.setFormatter(formatter)
    # add the handler to the root logger
    logging.getLogger('').addHandler(console)

    # Starting program
    try:
        if len(sys.argv) > 1:           # Checks to see if sys.argv has input
            argv = str(sys.argv[1])
            # purges logs
            if argv == '-p':
                purge_log()
                new_program()
            elif argv == '--purge':
                purge_log()
                new_program()
            else:
                # Raising Custom exemption
                raise InvalidArgumentException("User entered " + argv + " as invalid argument.")
        else:
            new_program()

    except InvalidArgumentException as err:
        log_specifics_debug('INVALID ARGV', err)
        sys.exit()

# **** End Program