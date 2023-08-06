# -*- coding: utf-8 -*-
# core.py
#
# Core class and function definitions

import os
import sys
import datetime
import socket
import pickle
import time
import subprocess
import shlex
import copy

TIME_OUT = 5.0
"""float: how long the socket waits before failing when sending data
"""

USER_DATA_DIR = '~/.neronet' # Remember to os.path.expanduser
USER_DATA_DIR_ABS = os.path.expanduser(USER_DATA_DIR)

MANDATORY_FIELDS = set(['run_command_prefix', 'main_code_file', 'parameters', 
                        'parameters_format'])
OPTIONAL_FIELDS = set(['outputs', 'collection', 'required_files',
                        'conditions', 'sbatch_args'])
AUTOMATIC_FIELDS = set(['path', 'time_created', 'time_modified', 'state', 
                        'cluster_id', 'warnings'])



class Cluster(object):
    """ 
    Attributes:
        cid (str): The unique ID (name) of the cluster
        ctype (str): Type of the cluster. Either slurm or unmanaged
        ssh_address (str): SSH address or config hostname corresponding to
            the cluster.
        sbatch_args (str): Slurm SBATCH arguments.
    """

    class Type:
        unmanaged = 'unmanaged'
        slurm = 'slurm'
        _members = set(['slurm', 'unmanaged'])
        @classmethod
        def is_member(cls, arg):
            return arg in cls._members

    def __init__(self, cid, ctype, ssh_address, sbatch_args=None):
        self.cid = cid
        self.ctype = ctype
        self.ssh_address = ssh_address
        self.sbatch_args = sbatch_args
        self.dir = USER_DATA_DIR

    def __str__(self):
        return '%s (%s, %s)' % (self.cid, self.ctype, self.ssh_address)

    def sshrun(self, cmd, inp=None):
        """Execute a shell command via SSH on the remote Neronet cluster."""
        # Ask SSH to execute a command that starts by changing the working
        # directory to 'self.dir' at the machine served at the specified
        # address and port
        scmd = 'ssh %s "cd %s;' % (self.ssh_address, self.dir)
        # Potentially include initialization commands depending on cluster
        # type
        if self.ctype == self.Type.unmanaged:
            pass
        elif self.ctype == self.Type.slurm:
            # Load the python 2.7 module to gain access to the interpreter
            scmd += ' module load python/2.7.4;'
        # Run the given command with the PATH and PYTHONPATH environment
        # variables defined to include the neronet executables and modules
        scmd += ' PATH="%s/neronet:/usr/local/bin:/usr/bin:/bin" PYTHONPATH="%s" %s"' \
                % (self.dir, self.dir, cmd)
        # Actual execution
        res = osrunroe(scmd, inp=inp)
        if res.rv != 0:
            msg = ''
            if res.err: msg += '\nErr: %s' % (res.err)
            if res.out: msg += '\nOut: %s' % (res.out)
            raise RuntimeError('Failed to run "%s" via SSH at cluster "%s"!%s'
                % (cmd, self.cid, msg))
        return res
        # PATH="$HOME/.neronet/neronet:/usr/local/bin:/usr/bin:/bin" PYTHONPATH="$HOME/.neronet"

    def test_connection(self):
        res = self.sshrun('python -V')
        if res.rv != 0:
            raise RuntimeError('Failed to run Python via SSH at "%s"!' % (self.cid))
        elif not res.err.startswith('Python 2.7'):
            raise RuntimeError('Incorrect Python version at "%s": "%s"!' % (self.cid, res.err))
        return True

    def start_neromum(self):
        res = self.sshrun('neromum --start')
        print('Neromum daemon started...')
        #print('Finished: %d, "%s", "%s"' % (res.rv, res.err, res.out))

    def clean_experiments(self, exceptions):
        data = {'action': 'clean_experiments', 'exceptions': exceptions}
        res = self.sshrun('neromum --input', inp=pickle.dumps(data, -1))
        print(res.out)
        if res.err:
            print('Error: %s\n' % (res.err))

    def yield_status(self):
        data = {'action': 'fetch', 'msg': 'I love honeybees!'}
        res = self.sshrun('neromum --input', inp=pickle.dumps(data, -1))
        yield 'Finished: %d, "%s", "%s"' % (res.rv, res.err, res.out)

class Experiment(object):
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
        cluster_id (str): The ID of the cluster where the experiment is run
        time_created (datetime): Timestamp of when the experiment was created
        time_modified (datetime): Timestamp of when the experiment was modified
        last
        path (str): Path to the experiment folder
    """

    class State:
        #none = 'none'
        defined = 'defined'
        submitted = 'submitted'
        submitted_to_kid = 'submitted_to_kid'
        lost = 'lost'
        terminated = 'terminated'
        running = 'running'
        finished = 'finished'

    def __init__(self, experiment_id, run_command_prefix, main_code_file,
                    parameters, parameters_format, path, required_files=None,
                    outputs="stdout", collection=None, conditions=None, sbatch_args=None):
        now = datetime.datetime.now()
        fields = {'run_command_prefix': run_command_prefix,
                    'main_code_file': main_code_file,
                    'required_files': required_files if required_files else [],
                    'outputs': outputs if isinstance(outputs, list) else
                                [outputs],
                    'parameters': parameters,
                    'parameters_format': parameters_format,
                    'collection': collection,
                    'conditions': conditions,
                    'sbatch_args': sbatch_args,
                    'path': path,
                    'time_created': now,
                    'time_modified': now,
                    'states_info': [(Experiment.State.defined, now)],
                    'cluster_id': None,
                    'warnings' : [] }
        #MAGIC: Creates the attributes for the experiment class
        self.__dict__['_fields'] = fields
        #super(Experiment, self).__setattr__('_fields', fields)
        super(Experiment, self).__setattr__('_experiment_id', experiment_id)
    
    def get_action(self, logrow):
        init_action = ('no action', '')
        try:
            for key in self._fields['conditions']:
                action = self._fields['conditions'][key].get_action(logrow)
                if action == 'kill':
                    return (action, key)
                elif action != 'no action':
                    init_action = (action, key)
        except TypeError:
            return init_action
        return init_action
       
    def set_warning(self, warning):
        self._fields['warnings'].append(str(datetime.datetime.now()) + ": The condition '" + warning + "' was met")
    
    def set_multiple_warnings(self, warnings):
        self._fields['warnings'] = warnings
            
    def has_warnings(self):
        if self._fields['warnings']:
            return 'WARNING'
        else:
            return ''
    
    def get_warnings(self):
        return self._fields['warnings']

    def __getattr__(self, attr):
        """Getter for the experiment class hides the inner dictionary"""
        #Gets the inner dictionary
        fields = super(Experiment, self).__getattribute__('_fields')
        if attr in fields:
            return fields[attr]
        #Gets hidden attributes by adding _
        if attr == 'id':
            attr = 'experiment_id'
        elif attr == 'state':
            return fields['states_info'][-1][0]
        elif attr == 'state_info':
            return fields['states_info'][-1]
        return super(Experiment, self).__getattribute__('_' + attr)

    def __setattr__(self, attr, value):
        """Setter for the experiment class
        
        Raises:
            AttributeError: if the attribute doesn't exist
        """
        #Gets the inner dictionary
        fields = super(Experiment, self).__getattribute__('_fields')
        if attr == 'id' or attr == 'experiment_id':
            super(Experiment, self).__setattr__('_experiment_id', value)
        elif attr in fields or attr in ('log_output', ):
            fields[attr] = value
        else:
            raise AttributeError('Experiment has no attribute named "%s"!' % attr)

    @property 
    def callstring(self):
        rcmd = self._fields['run_command_prefix']
        code_file = self._fields['main_code_file']
        parameters = self._fields['parameters']
        param_format = self._fields['parameters_format']
        parameters_string = param_format.format(**parameters)
        callstring = ' '.join([rcmd, code_file, parameters_string])
        return callstring

    def update_state(self, state):
        """ Updates the state
        """
        if state == self.state: return
        if state == 'running' and self._fields['conditions']:
            for c in self._fields['conditions']:
                self._fields['conditions'][c].start_time = datetime.datetime.now()
        self._fields['states_info'].append((state, datetime.datetime.now()))

    def as_dict(self):
        """ Returns the experiment as a dictionary
        """
        return {self._experiment_id: copy.deepcopy(self._fields)}

    def as_gen(self):
        """Creates a generate that generates info about the experiment
        Yields:
            str: A line of experiment status
        """
        yield "%s\n" % self._experiment_id
        yield "  Run command: %s\n" % self._fields['run_command_prefix']
        yield "  Main code file: %s\n" % self._fields['main_code_file']
        params = self._fields['parameters_format'].format( \
            **self._fields['parameters'])
        yield "  Parameters: %s\n" % params
        yield "  Parameters format: %s\n" % self._fields['parameters_format']
        if self._fields['collection']:
            yield "  Collection: %s\n" % self._fields['collection']
        yield "  State: %s\n" % self.state
        if self._fields['cluster_id']:
            yield "  Cluster: " + self._fields['cluster_id'] + '\n'
        yield "  Last modified: %s\n" % self._fields['time_modified']
        if self._fields['conditions']:            
            conds = '  Conditions:\n'
            for condition in self._fields['conditions']:
                conds +=  '    ' + self._fields['conditions'][condition].name + ':\n'
                conds +=  '      variablename: ' + self._fields['conditions'][condition].varname + '\n'
                conds +=  '      killvalue: ' + str(self._fields['conditions'][condition].killvalue) + '\n'
                conds +=  '      comparator: ' + self._fields['conditions'][condition].comparator + '\n'
                conds +=  '      when: ' + self._fields['conditions'][condition].when + '\n'
                conds +=  '      action: ' + self._fields['conditions'][condition].action + '\n'
            yield conds
        if self._fields['warnings']:
            warns = '  Warnings:\n'
            for warn in self._fields['warnings']:
                warns += '    ' + warn + '\n'
            yield warns

    def __str__(self):
        return "%s %s" % (self._experiment_id, self._fields['state'][-1][0])

class Runresult: """A class for holding shell command execution results."""

def osrunroe(cmd, vrb=True, inp=None):
    """Execute a shell command and return the return code, stdout and -err.

    Args:
        vrb (boolean): Whether to print command or not.
        inp (str): Input string for the sub process.

    Returns
        Runresult: The result object of the executed command.
    """
    if vrb: print('> %s' % (cmd))
    if type(cmd) == str:
        cmd = shlex.split(cmd)
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, stdin=subprocess.PIPE)
    res = Runresult()
    res.cmd = cmd
    res.out, res.err = proc.communicate(inp)
    res.rv = proc.poll()
    return res

def osrun(cmd, vrb=True):
    res = osrunroe(cmd, vrb)
    if res.rv != 0:
        raise RuntimeError('osrun(%s) failed! Err: "%s", Out: "%s".' \
                % (res.cmd, res.err, res.out))
    return res

def osrunq(cmd):
    return osrun(cmd, vrb=False)

def get_hostname():
    return osrunq('hostname').out.strip()

def time_now():
    return datetime.datetime.now() #.strftime('%H:%M:%S %d-%m-%Y')

def write_file(filepath, data):
    text = str(data)
    with open(filepath, 'w') as f:
        f.write(text)

def read_file(filepath, default=None):
    result = default
    try:
        with open(filepath, 'r') as f:
            result = ''
            for line in f:
                result += line
    except IOError as e:
        pass
    return result

def create_config_template():
    # Creates an empty experiment config file with the required fields.
    if os.path.exists('template.yaml'):
        print('A config template already exists in this folder.')
        return
    with open('template.yaml', 'w') as f:
        f.write('###Mandatory fields###\n')
        for field in MANDATORY_FIELDS:
            f.write('%s: \n' % field)
        f.write('###Optional fields###\n')
        for field in OPTIONAL_FIELDS:
            f.write('%s: \n' % field)
        
WARNING_FIELDS = set(['variablename', 'killvalue', 'comparator', 'when', \
                        'action'])

class ExperimentWarning:
    
    def __init__(self, name, variablename, killvalue, comparator, when, action):
        self.name = name.strip()
        self.varname = variablename.strip()
        self.killvalue = killvalue
        self.comparator = comparator.strip()
        self.when = when.strip()
        self.action = action.strip()
        self.start_time = datetime.datetime.now()
            
    def get_action(self, logrow):
        logrow = logrow.strip()
        varlen = len(self.varname)
        check_condition = True
        if 'time' in self.when:
            time_when = float(self.when[4:].strip())
            time_passed = datetime.datetime.now() - self.start_time
            time_passed_sec = time_passed.days * 86400 + time_passed.seconds
            time_passed_min = time_passed_sec / 60
            if time_passed_min < time_when:
                check_condition = False
        if check_condition and logrow[:varlen].strip() == self.varname:
            varvalue = logrow[varlen:].strip()
            try:
                varvalue = float(varvalue)
            except:
                return 'no action'
            if any( [self.comparator == 'gt' and varvalue > self.killvalue,
                self.comparator == 'lt' and varvalue < self.killvalue,
                self.comparator == 'eq' and varvalue == self.killvalue,
                self.comparator == 'geq' and varvalue >= self.killvalue,
                self.comparator == 'leq' and varvalue <= self.killvalue] ):
                return self.action
        return 'no action'

    def __eq__(self, other):
        if not other:
            return False
        for value in ['name', 'varname', 'killvalue', 'comparator', 'when', 'action']:
            if getattr(self, value) != getattr(other, value): return False
        return True
