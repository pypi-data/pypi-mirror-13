#!\usr\bin\env python
"""# Script name           :""" {{scriptName}}
"""# Author			    : """{{author}}
"""# Created              : """{{date}}
"""# Last Modified        : """{{date}}
"""# Version			    : 0.1"""

# Classes imported
import logging
import os


# Classes created




# **** Constants ****
LOG_FILE = ""      # Log file





# ***** Functions ***




# Utilities
def clear_screen():  # Function to clear the screen
    if os.name == "posix":  # Unix/Linux/MacOS/BSD/etc
        return os.system("clear")  # Clear the Screen
    elif os.name in ("nt", "dos", "ce"):  # DOS/Windows
        return os.system("CLS")


# Loggers
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


# *** Ends Functions

# *** Start Program
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