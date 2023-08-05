# -*- coding: utf-8 -*-
"""This module defines Nerokid.

Attributes:
  INTERVAL (float): interval for how long the kid waits until it rechecks
    for changes in the log file
  LOG_FILES (tuple): Log files for stdout and stderr
"""
import sys
import os
import time
import subprocess
import shlex

import neronet.core

INTERVAL = 2.0
LOG_FILES = 'stdout.log', 'stderr.log'
packet = {"running": True, "log_output": ""}
commands = ("status")


class LogFile(object):

    """A class that facilitates efficient monitoring of logfile changes."""

    def __init__(self, path):
        """Create a LogFile object to represent a log file.

        Args:
            path (str): the file path to the log file.
        """
        self.path = path
        self.rtime = 0
        self.seek = 0

    def read_changes(self):
        """Read changes made to the logfile."""
        mtime = os.stat(self.path).st_mtime
        if mtime > self.rtime:
            self.rtime = mtime
            with open(self.path, 'r') as stream:
                stream.seek(self.seek)
                changes = stream.read()
                self.seek = stream.tell()
                return changes


class NeroKid(object):

    """A class to specify the Nerokid object.

    Runs in a cluster node and manages and monitors the experiment given.

    Gets host as the 1st command line argument
    Port as the 2nd
    Experiment as the 3rd
    Experiment parameters from 4th argument onwards
    """

    def __init__(self):
        self.sock = None
        self.process = None
        self.logger = neronet.core.Logger('KID')
        self.experiment = ' '.join(sys.argv[3:])
        self.log_files = [LogFile(log_file_path)
                          for log_file_path in LOG_FILES]

    def run(self):
        """The Nerokid main.

        Initializes the socket, launches the child process and starts to monitor the child process
        """
        self.logger.log('Kid launched!')
        self.initialize_socket()
        self.logger.log('Launching the experiment...')
        self.launch_child_process()
        self.monitor_process()
        self.logger.log('Process finished!')

    def initialize_socket(self):
        """initialize socket with command line arguments for host and port"""
        host, port = sys.argv[1:3]
        port = int(port)
        # Define a socket
        self.sock = neronet.core.Socket(self.logger, host, port)
        self.logger.log('- Mom address: (%s, %d)' % (host, port))
        self.logger.log('- Experiment: %s' % (self.experiment))

    def send_data_to_neromum(self, text):
        """Send status data to Neromum."""
        self.sock.send_data(text)

    def launch_child_process(self):
        """Launches received script"""
        self.process = subprocess.Popen(
            shlex.split(
                self.experiment), universal_newlines=True, stdout=open(
                'stdout.log', 'w'), stderr=open(
                'stderr.log', 'w'), close_fds=True, bufsize=1)

    def monitor_process(self):
        """Writes information about the process into a log file on set intervals"""
        self.logger.log('- Experiment PID: %s' % (self.process.pid))
        packet["running"] = True
        while self.process.poll() == None:
            # Sleep to wait for changes
            time.sleep(INTERVAL)
            self.collect_new_file_data()
        packet["running"] = False
        self.send_data_to_neromum(packet)

    def collect_new_file_data(self):
        """Collect any data that the child process outputs and send them to neromum"""
        # Check for any new log output
        log_output = {}
        for log_file in self.log_files:
            changes = log_file.read_changes()
            if changes:
                log_output[log_file.path] = changes
        # Send any new log output to Mum
        if log_output:
            packet["log_output"] = log_output
            self.send_data_to_neromum(packet)

    def terminate_process(self):
        """Terminate the experiment"""
        self.process.kill()
        self.logger.log('- Experiment PID: %s terminated' % (self.process.pid))


def main():
    """Create a Nerokid and call its run method."""
    NeroKid().run()
