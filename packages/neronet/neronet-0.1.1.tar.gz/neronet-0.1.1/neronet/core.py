# core.py
#
# Core class and function definitions

import os
import sys
import datetime
import socket
import pickle
import time
#import psutil
from signal import signal, SIGTERM, SIGQUIT
from traceback import print_exc
from pathlib import Path

TIME_OUT = 5.0
"""float: how long the socket waits before failing when sending data
"""
MANDATORY_FIELDS = set(['run_command_prefix', 'main_code_file', 'parameters', 
                        'parameters_format'])
OPTIONAL_FIELDS = set(['logoutput', 'collection', 'required_files',
                        'conditions'])
AUTOMATIC_FIELDS = set(['path', 'time_created', 'time_modified', 'state', 
                        'cluster'])

class Experiment:
    """ 
    Attributes:
        experiment_id (str): Unique identifier to the experiment
        run_command_prefix (str): The run command of the experiment
        main_code_file (str): The code file to be run
        required_files (str): Other files required by the experiments
        logoutput (str): File where the experiment outputs information
        parameters (dict): The Experiment parameters
        parameters_format (str): The format of the experiment parameters
        collection (str): The collection the experiment is part of
        conditions (dict): Special condition for the experiment to do stuff
        state (list of tuples): The states of the experiment with timestamp
        cluster (str): The cluster where the experiment is run
        time_created (str): Timestamp of when the experiment was created
        time_modified (str): Timestamp of when the experiment was modified
        last
        _path (str): Path to the experiment folder
    """
    def __init__(self, experiment_id, run_command_prefix, main_code_file,
                    parameters, parameters_format, path, required_files=[],
                    logoutput='output.log', collection=None, conditions=None):
        self.experiment_id = experiment_id
        now = self._time_now()
        self.fields = {'run_command_prefix': run_command_prefix,
                        'main_code_file': main_code_file,
                    'required_files': required_files,
                    'logoutput': logoutput,
                    'parameters': parameters,
                    'parameters_format': parameters_format,
                    'collection': collection,
                    'conditions': conditions,
                    'path': path,
                    'time_created': now,
                    'time_modified': now,
                    'state': [['defined', now]],
                    'cluster': None}
    
    def get_callstring(self):
        rcmd = self.fieds['run_command_prefix']
        code_file = self.fields['main_code_file']
        parameters = self.fields['parameters']
        param_format = self.fields['parameters_format']
        parameters_string = param_format(**parameters)
        callstring = ' '.join(rcmd, code_file, parameters_string)
        return callstring

    def update_state(self, state):
        """ Updates the state
        """
        self.fields['state'].append([state, self._time_now()])

    def as_dict(self):
        """ Returns the experiment as a dictionary
        """
        return {self.experiment_id: self.fields}

    def _time_now(self):
        """ A helper function to save the current time in consistend format

        Return:
            The current time as a string
        """
        return datetime.datetime.now().strftime('%H:%M:%S %d-%m-%Y')

    def __str__(self):
        return "%s %s" % (self.experiment_id, self.fields['state'][-1][0])

def osrun(cmd):
    print('> %s' % (cmd))
    os.system(cmd)


class Logger:

    """A class to simplify logging."""

    def __init__(self, name):
        self.name = name

    def log(self, msg):
        """prints datetime, process name, process message"""
        # Print to stdout in a clear format
        print('%s %s: %s' % (datetime.datetime.now(), self.name, msg))


class Socket:

    """A class to simplify socket usage."""

    def __init__(self, logger, host, port):
        # Save key attributes
        self.logger = logger
        self.host = host
        self.port = port

    def send_data(self, data):
        """Create a socket, send data over it, and close it"""
        # Create a TCP/IP socket
        sock = socket.socket()
        sock.settimeout(TIME_OUT)
        # Connect to the mother
        #self.logger.log('Connecting to (%s, %s)...' % (self.host, self.port))
        sock.connect((self.host, self.port))
        # Send data
        #self.logger.log('Sending data "%s"...' % (data))
        sock.sendall(pickle.dumps(data, -1))
        # Close socket
        #self.logger.log('Closing socket...')
        sock.close()

