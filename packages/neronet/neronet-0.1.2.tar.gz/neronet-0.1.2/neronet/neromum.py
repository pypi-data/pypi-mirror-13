# -*- coding: utf-8 -*-
"""This module defines Neromum.
"""

# TODO: need database parsing

import sys
import socket
import os
import pickle
import select

import neronet.core

class Neromum(object):

    """A class to specify the Neromum object.

    Runs in the cluster and manages and monitors all the nodes.

    Gets the experiment as the 1st command line argument
    Experiment parameters from 2nd onwards.
    """

    def __init__(self):
        self.sock = None
        self.experiment = ' '.join(sys.argv[1:])
        self.logger = neronet.core.Logger('MUM')
        self.running = True
        self.open_incoming_connections = []
        self.open_outgoing_connections = []

    def run(self):
        """The Neromum main."""
        self.logger.log('Creating the socket')
        self.initialize_socket()
        # self.send_experiment_to_node()
        self.start_nerokid()
        # self.start_nerokid2()
        self.listen_loop()
        self.logger.log('Shutting down')
        self.sock.shutdown(socket.SHUT_RDWR)

    def initialize_socket(self):
        """Creates the socket and sets it to listen"""
        self.sock = socket.socket()
        self.sock.settimeout(5.0)
        # Bind the socket to localhost, auto choose port
        self.sock.bind(('localhost', 0))
        # Put the socket into server mode
        self.sock.listen(1)
        # Retrieve socket specs
        self.host, self.port = self.sock.getsockname()
        self.open_incoming_connections.append(self.sock)

    def save_to_file(self, data, file):

        pass

    def start_nerokid(self):
        """Starts the nerokid in the node"""
        self.logger.log('Launching kids')
        self.logger.log(sys.argv)
        neronet.core.osrun(
            'nerokid %s %d %s &' %
            (self.host, self.port, self.experiment))

    def send_data_to_neroman(self):
        pass

    def send_experiment_to_node(self):
        pass

    def kill_child(self):
        pass

    def ask_slurm_for_free_node(self):
        pass

    def parse_nerokid_data(self):
        """Extract information from nerokid's data updates."""
        if self.data:
            self.data = pickle.loads(self.data)
            if isinstance(self.data, dict):
                for log_path, new_text in self.data['log_output'].items():
                    self.logger.log('New output in %s:' % (log_path))
                    for ln in new_text.split('\n'):
                        if not ln:
                            continue
                        self.logger.log('    %s' % (ln.strip()))
                if not self.data["running"]:
                    self.logger.log('Kid has finished!')
                    # delete later when finished testing. (ie mom is working as
                    # daemon)
                    self.running = False

    def listen_loop(self):
        """Listen to the socket from nerokid and receive data"""
        while self.running:
            inRdy, outRdy, excpRdy = select.select(
                self.open_incoming_connections, [], [])
            for s in inRdy:
                if s == self.sock:
                    client, address = s.accept()
                    self.open_incoming_connections.append(client)
                else:
                    self.data = s.recv(4096)
                    if self.data:
                        self.parse_nerokid_data()
                    else:
                        s.close()
                        self.open_incoming_connections.remove(s)

def main():
    """Create a Neromum and call its run method."""
    Neromum().run()
