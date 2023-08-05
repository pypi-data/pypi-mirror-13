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


class Daemon(object):

    """A generic daemon class.

    See:
    - https://www.python.org/dev/peps/pep-3143/
    - https://docs.python.org/3.5/library/socketserver.html
    - http://stackoverflow.com/questions/15652791/how-to-create-a-python-socket-listner-deamon
    """

    class NoPidFileError(Exception):
        pass

    def __init__(self, name):
        self.name = name
        self.pd = Path.home() / '.neronet' / self.name
        self.pfout = self.pd / 'out'
        self.pferr = self.pd / 'err'
        self.pfpid = self.pd / 'pid'
        self.pfport = self.pd / 'port'
        self.pd.mkdir(parents=True, exist_ok=True)
        self.port = 0
        self.tdo = 5
        self.sckt = None

    def log_form(self, prefix, message):
        return '%s %s  %s\n' % (prefix,
                                time.strftime(
                                    '%Y-%m-%d %H:%M:%S',
                                    time.localtime()),
                                message)

    def log(self, message):
        sys.stdout.write(self.log_form('LOG', message))

    def wrn(self, message):
        sys.stdout.write(self.out('WRN', message))

    def err(self, message, err=None):
        output = self.log_form('ERR', message)
        # sys.stdout.write(output)
        if err:
            sys.stderr.write(output)
            print_exc()
            sys.stderr.write('\n')
        else:
            sys.stderr.write(output)

    def _read_i_or_nan(self, pf):
        try:
            return int(pf.read_text())
        except:
            return None

    def rpfpid(self):
        self.pid = self._read_i_or_nan(self.pfpid)
        return self.pid

    def rpfport(self):
        self.port = self._read_i_or_nan(self.pfport)
        return self.port

    def get_process(self):
        # Get the pid from the pfpid
        pid = self.rpfpid()
        if pid is None:
            return None
        try:
            proc = psutil.Process(pid)
            if 'nero' not in proc.name():
                raise psutil.NoSuchProcess
        except psutil.NoSuchProcess:
            self.err("is_running(): The pid file is deprecated!")
            self.cleanup()
            return None
        if proc.is_running():
            return proc

    def is_running(self):
        return self.get_process() != None

    def cleanup(self, outfiles=False):
        """Remove daemon instance related files."""
        self.log("cleanup(): Removing instance related files...")
        files = [self.pfpid, self.pfport] + \
            [self.pfout, self.pferr] if outfiles else []
        for pf in files:
            if pf.exists():
                self.log('cleanup(): Removing "%s"...' % (pf))
                pf.unlink()

    def quit(self):
        self.cleanup()
        self.log("quit(): Exiting... Bye!")
        sys.exit(0)

    def recv_signal(self, sign, frme):
        self.log('recv_signal(): Received signal "%s"!' % (sign))
        if sign in (SIGTERM, SIGQUIT):
            self.quit()

    def daemonize(self):
        """Daemonize the process.

        Essentially
        - Daemonizes the process by double forking
        - Redefines a few variables and a few handles to unix signals
        - Defines stdout, stderr and logging streams
        - Writes the pid file
        """

        # Exit first parent (first fork)
        self.log("daemonize(): Daemonizing the process...")
        try:
            pid = os.fork()
            if pid > 0:
                sys.exit(0)
        except OSError as err:
            self.err('daemonize(): Fork #1 failed!', err=err)
            sys.exit(1)

        # Decouple from parent environment
        os.chdir(str(self.pd))
        os.setsid()
        os.umask(0)

        # Do second fork
        try:
            pid = os.fork()
            if pid > 0:
                sys.exit(0)
        except OSError as err:
            self.err('daemonize(): Fork #2 failed!', err=err)
            sys.exit(1)

        # Redirect standard file descriptors
        sys.stdout.flush()
        sys.stderr.flush()
        so = self.pfout.open('w', encoding='utf-8')
        se = self.pferr.open('w', encoding='utf-8')
        os.dup2(so.fileno(), sys.stdout.fileno())
        os.dup2(se.fileno(), sys.stderr.fileno())

        # Update PID
        self.pid = os.getpid()
        self.pfpid.write_text(str(self.pid))

        # Add signal handlers
        self.log('daemonize(): Adding a signal handler...')
        signal(SIGTERM, self.recv_signal)
        signal(SIGQUIT, self.recv_signal)

        # Print encoding info
        import locale
        self.log(
            'daemonize(): Active encodings: %s, %s...' %
            (sys.getfilesystemencoding(), locale.getpreferredencoding()))

    def start(self):
        """Start the daemon."""
        # Check for a pfpid to see if the daemon already runs
        if self.is_running():
            self.err('start(): The daemon is already running!')
            sys.exit(1)
        self.log('start(): Starting the daemon...')
        # Remove old files...
        self.cleanup(outfiles=True)
        # Start the daemon
        self.daemonize()
        self.log('start(): Executing run...')
        self.run()

    def stop(self):
        """Stop the daemon."""
        self.log('stop(): Stopping the daemon...')
        proc = self.get_process()
        if proc:
            proc.send_signal(SIGQUIT)
            time.sleep(0.4)
            self.log("stop(): Daemon terminated!")
        if self.pfpid.exists():
            self.err("stop(): The daemon failed to cleanup!")
            self.cleanup()

    def restart(self):
        """Restart the daemon."""
        self.log("restart(): Restarting the daemon...")
        try:
            self.stop()
        except self.NoPidFileError:
            pass
        self.start()

    def run(self):
        """The daemon process loop."""
        # Socket Initialization
        self.sckt = gsocket(self.port, self.tdo)
        # Port
        self.port = self.sckt.getsockname()[1]
        self.pfport.write_text(str(self.port))
        # Init callback
        self.daemon_init()
        # The Loop
        r = 0
        self.log('run: listening port %d (to: %s, pid: %d)...' %
                 (self.port, self.tdo, self.pid))
        while True:
            out = None
            try:
                out = listenfordata(self.sckt)
            except Exception as err:
                self.err("run: listen error:\n%s\n" % (err))
            if out:
                dta, address = out
                ip, port = address
                self.log("run: msg from %s:%s: |%s|" % (ip, port, dta))
                self.onreceive(ip, port, dta)
            else:
                # Ontdo callback
                self.ontdo()

    def respond(self, ip, port, reply, args=()):
        sndreply(port, reply, args, self.sckt)

    def daemon_init(self):
        """
        You should override this method when you subclass the Daemon. It
        can be used to init the daemon as it will be called before the process
        enters the loop. It is executed also on restarts!
        """
        self.log("LD::init: WARNING: No init specified!!!")

    def onreceive(self, adda, addb, sin):
        """
        You should override this method when you subclass Daemon. It will be called after the process receives input
        """
        self.log("LD::onreceive: ERROR: No onreceive specified!!!")
        raise Exception("ERROR: No onreceive specified!!!")

    def ontdo(self):
        """
        You should override this method when you subclass Daemon. It will be called if the process does not receive input
        """
        self.log("LD::ontdo: nothing received...")
