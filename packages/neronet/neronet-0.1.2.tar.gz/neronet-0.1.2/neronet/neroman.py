# -*- coding: utf-8 -*-
"""This module defines Neroman.

To work with Neroman each experiment must have the following attributes
defined in its config:

* experiment_id: The unique identifier for the experiment
* run_command_prefix: The run command of the experiment
* main_code_file: The code file to be run
* destination_folder: Folder that the experiment is run in on the cluster.
* parameters: The definition of the experiment parameters
* parameters_format: The format of the experiment parameters
* logoutput: The location the experiment outputs its output
* state: A tuple of the experiment state which is set to 'defined' by this
  function and the time changed
* cluster: The cluster that the experiment is running on. Set to
  None by this function
* time_created: Sets the current time as the creation time
* time_modified: The time the experiment was last modified. Sets
  this time to the same as the time created
* path: The absolute path to the folder

"""

import os
import time
import datetime
import pathlib

import yaml

import neronet.core
import neronet.config_parser

class Neroman:

    """The part of Neronet that handles user side things.

    Attributes:
        database (str): Path to the database used, currently only .yaml
        clusters (Dict): A dictionary containing the specified clusters
        experiments (Dict): A dictionary containing the specified experiments
        preferences (Dict): A dictionary containing the preferences
    """

    def __init__(self, database='default.yaml',
                 preferences_file='preferences.yaml',
                 clusters_file='clusters.yaml'):
        """Initializes Neroman

        Reads the contents of its attributes from a database (currently just
        a .yaml file).

        Args:
            database (str): The path to the database file as a string, the
                rest of the attributes will be parsed from the database.
        """
        self.database = database
        self.clusters_file = clusters_file
        self.preferences_file = preferences_file
        self.config_parser = neronet.config_parser.ConfigParser()
        self.clusters = {}
        self.experiments = {}
        self.preferences = {}
        self._load_configurations(database, clusters_file, preferences_file)

    def _load_configurations(self, database, clusters, preferences):
        """Load the configurations from the yaml files or creates them if they
        don't exist

        Args:
            database (str): The filepath of the database file
            clusters (str): The filepath of the clusters file
            preferences (str): The filepath of the preferences file
        """
        if not os.path.exists(preferences):
            with open(preferences, 'w') as f:
                f.write("name:\nemail:\n")
        else:
            with open(preferences, 'r') as f:
                self.preferences = yaml.load(f.read())
        if not self.preferences:
            self.specify_user("","")
        if 'default_cluster' not in self.preferences:
            self.preferences['default_cluster'] = ""
        if 'email' not in self.preferences:
            raise FormatError('The user\'s email is not specified')
        if 'name' not in self.preferences:
            raise FormatError('The user\'s name is not specified')

        if not os.path.exists(clusters):
            with open(clusters, 'w') as f:
                f.write("clusters:\ngroups:\n")
        else:
            with open(clusters, 'r') as f:
                self.clusters = yaml.load(f.read())
        if not self.clusters:
            self.clusters = {'clusters': None}
        if not self.clusters['clusters']:
            self.clusters['clusters'] = {}
        
        # This checks the format of the clusters file            
        for key in self.clusters['clusters']:
            if 'type' not in self.clusters['clusters'][key]:
                self.clusters['clusters'][key]['type'] = 'unmanaged'
            else:
                if self.clusters['clusters'][key]['type'] != 'unmanaged':
                    if self.clusters['clusters'][key]['type'] != 'slurm':
                        raise FormatError('The cluster type for the cluster ' +
                        key + ' is not valid.')
            if 'port' not in self.clusters['clusters'][key]:
                self.clusters['clusters'][key]['port'] = 22
            if 'ssh_address' not in self.clusters['clusters'][key]:
                raise FormatError('The ssh address for the cluster ' + key + 
                ' is not defined.')
        if self.preferences['default_cluster']:
            if self.preferences['default_cluster'] not in self.clusters['clusters']:
                raise FormatError('The specified default cluster ' + 
                self.preferences['default_cluster'] +' is not found')
                
        with open(self.clusters_file, 'w') as f:
            f.write(yaml.dump(self.clusters, default_flow_style=False))

        if not os.path.exists(database):
            with open(database, 'w') as f:
                f.write('')
        else:
            with open(database, 'r') as f:
                self.experiments = yaml.load(f.read())
        if not self.experiments:
            self.experiments = {}

    def save_database(self):
        """Save the contents of Neroman's attributes in the database
        """
        with open(self.database, 'w') as f:
            f.write(yaml.dump(self.experiments,
                              default_flow_style=False))

    def specify_cluster(
            self,
            cluster_name,
            ssh_address,
            cluster_type,
            portnumber=22):
        """Specify clusters so that Neroman is aware of them.

        Writes cluster name, address and type to the clusters config file

        Args:
            cluster_name (str): The name of the cluster, should be unique
            ssh_address (str): SSH address of the cluster
            cluster_type (str): Type of the cluster. Either slurm or unmanaged

        Raises:
            FormatError: if the cluster type isn't unmanaged or slurm

        """
        if cluster_type != 'slurm' and cluster_type != 'unmanaged':
            raise neronet.config_parser.FormatError( \
                        "Cluster type should be slurm or unmanaged")

        self.clusters['clusters'][cluster_name] = {'ssh_address': ssh_address,
                                                   'type': cluster_type,
                                                   'port': portnumber}
        with open(self.clusters_file, 'w') as f:
            f.write(yaml.dump(self.clusters, default_flow_style=False))

    def specify_experiments(self, folder):
        """Specify experiments so that Neroman is aware of them.

        Reads the contents of the experiment from a config file inside the
        specified folder.

        Args:
            folder (str): The path of the folder that includes
                the experiment that's being specified.

        Raises:
            FileNotFoundError: If the folder doesn't exists or the config file
                doesn't exists
            FormatError: If the config file is badly formated
        """


        experiments = self.config_parser.parse_experiments(folder)
        for experiment in experiments:
            if experiment.experiment_id in self.experiments:
                raise IOError("Experiment named %s already in the database" \
                                % experiment.experiment_id)
            else: self.experiments[experiment.experiment_id] = experiment
        self.save_database()

    def _time_now(self):
        return datetime.datetime.now().strftime('%H:%M:%S %d-%m-%Y')

    def update_state(self, experiment_id, state):
        self.experiments[experiment_id].update_state(state)

    def specify_user(self, name, email, default_cluster = ""):
        """Update user data"""
        self.preferences['name'] = name
        self.preferences['email'] = email
        self.preferences['default_cluster'] = default_cluster
        with open(self.preferences_file, 'w') as f:
            f.write(yaml.dump(self.preferences, default_flow_style=False))

    def get_experiment_results(self, experiment_id, remote_dir, local_dir):
        """Get the experiment results from neromum

        Args:
            experiment_id (str): the experiment ID.
            remote_dir (str): the file path to results folder on the remote
                machine.
            local_dir (str): the file path to results folder on the local
                machine.
        """
        experiment = self.experiments[experiment_id]
        cluster_ID = experiment.fields['cluster']
        cluster_port = self.clusters['clusters'][cluster_ID]['port']
        cluster_address = self.clusters['clusters'][cluster_ID]['ssh_address']
        neronet.core.osrun(
            'rsync -az -e "ssh -p%s" "%s:%s" "%s"'
            % (cluster_port, cluster_address,
                remote_dir, local_dir))

    def status(self, arg):
        """Display Neroman data on into stdstream"""
        if arg != 'all':
            if arg in self.experiments:
                experiment = self.experiments[arg]
                parameters = experiment.fields['parameters']
                time_modified = experiment.fields['time_modified']
                state, state_change_time = experiment.fields['state'][-1]
                parameters_string = ', '.join(
                    ["%s: %s" % (k, v) for k, v in parameters.items()])
                print(
                    'Experiment: %s\nParameters: %s' %
                    (arg, parameters_string))
                if state == 'defined':
                    print('State: %s - %s' % (state, state_change_time))
                else:
                    cluster = experiment['cluster']
                    print(
                        'State: %s - %s - %s' %
                        (state, cluster, state_change_time))
                print('Last modified: %s' % time_modified)
                return
            else:
                raise IOError('No experiment named %s' % arg)
        print("================Neroman=================")
        print("\n================User=================")
        print("Name: " + self.preferences['name'])
        print("Email: " + self.preferences['email'])
        if self.preferences['default_cluster']:
            print("Default Cluster: " + self.preferences['default_cluster'])
        print("\n================Clusters================")
        if not self.clusters['clusters']:
            print("No clusters defined")
        else:
            for cluster in self.clusters['clusters']:
                address = self.clusters['clusters'][cluster]['ssh_address']
                type = self.clusters['clusters'][cluster]['type']
                print("{} {} {}".format(cluster, address, type))
        print("\n================Experiments=============")
        if not len(self.experiments):
            print("No experiments defined")
        else:
            for experiment in sorted(self.experiments):
                print(self.experiments[experiment])

    def send_files(
        self,
        experiment_folder,
        remote_dir,
        cluster_address,
        cluster_port,
        neronet_root=pathlib.Path.cwd(),
    ):
        """Send experiment files to the cluster

        Args:
            experiment_folder (str): the file path to experiment folder on the local machine.
            remote_dir (str): the file path to experiment folder on the remote cluster.
            neronet_root (str): the file path to neronet folder.
            cluster_address (str): the address of the cluster.
            cluster_port (int): ssh port number of the cluster.
        """
        tmp_dir = pathlib.Path('/tmp/neronet-tmp')
        # rsync the neronet files to tmp
        neronet.core.osrun(
            'rsync -az "%s" "%s"' %
            (neronet_root /
             'neronet',
             tmp_dir))
        # rsync bin files to tmp
        neronet.core.osrun(
            'rsync -az "%s" "%s"' %
            (neronet_root / 'bin', tmp_dir))
        # rsync the experiment files to tmp
        neronet.core.osrun(
            'rsync -az "%s/" "%s"' %
            (experiment_folder, tmp_dir))
        neronet.core.osrun(
            'rsync -az -e "ssh -p%s" "%s/" "%s:%s"' %
            (cluster_port,
             tmp_dir,
             cluster_address,
             remote_dir))

    def submit(self, exp_id, cluster_ID = ""):
        """Main loop of neroman.

        Start the experiment in the cluster using ssh.

        Args:
            experiment_folder (str) : the file path to experiment folder in local machine.
            experiment_destination (str) : the file path to experiment folder on the remote cluster.
            experiment (str) : the name of the experiment.
            cluster_address (str) : the address of the cluster.
            cluster_port (int) : ssh port number of the cluster.
        """
        if not cluster_ID:
            cluster_ID = self.preferences['default_cluster']
            
        if cluster_ID not in self.clusters['clusters']:
            raise IOError('The given cluster ID or default cluster is not valid')
        
        remote_dir = pathlib.Path('/tmp/neronet-%d' % (time.time()))
        experiment_destination = self.experiments[exp_id].fields[
            'path'] + "/" + self.experiments[exp_id].fields['logoutput']
        experiment_folder = self.experiments[exp_id].fields["path"]
        #experiment = self.experiments[exp_id]["path"]+"/"+self.experiments[exp_id]["main_code_file"]
        experiment_parameters = self.experiments[exp_id].get_callstring()
        cluster_port = self.clusters['clusters'][cluster_ID]["port"]
        cluster_address = self.clusters["clusters"][cluster_ID]["ssh_address"]
        self.send_files(
            experiment_folder,
            remote_dir,
            cluster_address,
            cluster_port)
        # Magic do NOT touch:
        neronet.core.osrun(
            'ssh -p%s %s "cd %s; PATH="%s/bin:/usr/local/bin:/usr/bin:/bin" PYTHONPATH="%s" neromum %s"' %
            (cluster_port,
             cluster_address,
             remote_dir,
             remote_dir,
             remote_dir,
             experiment_parameters))
        self.experiments[exp_id].fields['cluster'] = cluster_ID
        self.update_state(exp_id, 'submitted')
        self.save_database()
        time.sleep(2)  # will be unnecessary as soon as daemon works
        # returns the results, should be called from cli
        self.get_experiment_results(exp_id, remote_dir, experiment_destination)
