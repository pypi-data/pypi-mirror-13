# -*- coding: utf-8 -*-
"""This module defines Neromum.
"""

# TODO: need database parsing

import os
import sys
import pickle
import glob
import time

import neronet.core
import neronet.daemon
import neronet.nerokid

class Neromum(neronet.daemon.Daemon):

    """A class to specify the Neromum object.

    Runs in the cluster and manages and monitors all the nodes.

    Gets the experiment as the 1st command line argument
    Experiment parameters from 2nd onwards.

    Attrs:
        exp_dict (dict): A dict of all experiments submitted to this mum by
            experiment ID.
    """

    def __init__(self):
        super(Neromum, self).__init__('neromum')
        self.exp_dict = {}
        self.add_query('list_exps', self.qry_list_exps)
        self.add_query('exp_update', self.qry_exp_update)
        self.add_query('exp_set_warning', self.qry_exp_warning)

    def qry_list_exps(self): # primarily for debugging
        """List all experiments submitted to this mum."""
        msg = 'Experiments:\n'
        for exp in self.exp_dict.values():
            msg += '- %s  %s  %s\n' % (exp.id, exp.state, exp.path)
        self._reply['msgbody'] = msg
        self._reply['rv'] = 0

    def qry_exp_update(self, exp_id, state, log_output):
        """Save information from Nerokids' experiment data updates."""
        exp = self.exp_dict[exp_id]
        # Extract log output update information
        for log_path, new_text in exp.log_output.items():
            # Initialize buffers for any new log path
            if log_path not in exp.log_output:
                exp.log_output[log_path] = ''
            # Append the new log output
            exp.log_output[log_path] += new_text
        # Update experiment state info
        exp.update_state(state)
        neronet.core.write_file(os.path.join(neronet.core.USER_DATA_DIR_ABS,
                'experiments', exp.id, 'exp.pickle'), pickle.dumps(exp))
        # Debugging
        if exp.state == neronet.core.Experiment.State.finished:
            self.log('Experiment "%s" has finished!' % (exp.id))
        self._reply['rv'] = 0
    
    def qry_exp_warning(self, exp_id, warnings):
        exp = self.exp_dict[exp_id]
        exp.set_multiple_warnings(warnings)
        neronet.core.write_file(os.path.join(neronet.core.USER_DATA_DIR_ABS,
                'experiments', exp.id, 'exp.pickle'), pickle.dumps(exp))

    def ontimeout(self):
        """Load and start any unstarted received experiments."""
        # Load all experiments into the dict that have not yet been loaded
        for exp_file in glob.glob(os.path.join(neronet.core.USER_DATA_DIR_ABS,
                'experiments/*/exp.pickle')):
            #self.log('Checking exp "%s"...' % (exp_file))
            exp_id = os.path.basename(os.path.dirname(exp_file))
            if exp_id not in self.exp_dict:
                exp = pickle.loads(neronet.core.read_file(exp_file))
                self.log('New experiment detected: "%s" (%s)...' % (exp_id, exp.state))
                self.exp_dict[exp_id] = exp
        # Start an experiment if there is any to start
        for exp in self.exp_dict.values():
            if exp.state == neronet.core.Experiment.State.submitted:
                # Initialize the log output container
                exp.log_output = {}
                # TODO: Allow sbatch launch
                # Launch experiment in the local (umanaged) node
                self.log('Launching experiment "%s"...' % (exp.id))
                nerokid = neronet.daemon.QueryInterface(neronet.nerokid.Nerokid(exp.id))
                # Start the kid daemon
                nerokid.start()
                # Wait until it gets initialized
                time.sleep(2.0)
                # Configure it
                nerokid.query('configure', host=self._host, port=self._port)
                exp.update_state(neronet.core.Experiment.State.submitted_to_kid)
                return # pace submission by launching only one at a time
        # Compute the number of finished experiments
        finished_count = 0
        for exp in self.exp_dict.values():
            if exp.state == neronet.core.Experiment.State.finished:
                finished_count += 1
        # Exit if all known (submitted) experiments are finished
        if finished_count == len(self.exp_dict):
            self.log('All %d experiments are finished. Quitting...' % (finished_count))
            self._doquit = True

def main():
    """Create a CLI interface object and process CLI arguments."""
    cli = neronet.daemon.Cli(Neromum())
    cli.parse_arguments()

#if __name__ == '__main__':
#    main()
