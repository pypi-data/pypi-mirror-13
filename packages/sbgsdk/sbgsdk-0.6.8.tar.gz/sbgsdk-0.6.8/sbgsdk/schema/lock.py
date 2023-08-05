__author__ = 'Sinisa'

import os
import time
import random
import logging

def lock(name):
    while True:
        try:
            os.mkdir(name + '.lock')
            return name + '.lock'
        except OSError:
            logging.exception("Error while locking file")
            time.sleep(random.random())


def unlock(name):
    os.rmdir(name + '.lock')
