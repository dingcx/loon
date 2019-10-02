# -*- coding: utf-8 -*-
"""Classes used in loon package"""

import sys
import os
import json
import pprint
import socket
from ssh2.session import Session
if __package__ == '' or __package__ is None:  # Use for test
    from __init__ import __host_file__
    from utils import create_parentdir, isfile, isdir
else:
    from loon import __host_file__
    from loon.utils import create_parentdir, isfile, isdir    

class Host:
    """
    Representation of remote host
    """
    def __init__(self, hostfile = __host_file__):
        self.hostfile = hostfile
        self.load_hosts()
        return

    def load_hosts(self):
        """Load hosts from file"""
        if not isfile(self.hostfile):
            self.active_host = []
            self.available_hosts = []
        else:
            with open(self.hostfile, 'r') as f:
                hosts = json.load(f)
            self.active_host = hosts['active']
            self.available_hosts = hosts['available']
        return

    def save_hosts(self):
        """Save hosts to file"""
        # if len(self.active_host)==0 or len(self.available_hosts)==0:
        #     raise ValueError("Cannot save to file due to null host.")
        hosts = {'active':self.active_host, 'available':self.available_hosts}
        if not isfile(self.hostfile):
            # Create parent dir if hostfile does not exist
            create_parentdir(self.hostfile)
        with open(self.hostfile, 'w') as f:
            json.dump(hosts, f)
        return

    def add(self, username, host, port=22):
        """Add a remote host"""
        info = [username, host, port]

        if info in self.available_hosts:
            print("=> Input host exists. Will not change.")
            return
        else:
            self.available_hosts.append(info)
            if len(self.active_host) == 0:
                self.active_host = info
            self.save_hosts()
            print("=> Added successfully!")
        return

    def delete(self, username, host, port=22):
        """Delete a remote host"""
        info = [username, host, port]
        if info in self.available_hosts:
            print("=> Removing host from available list...")
            self.available_hosts.remove(info)
            if info == self.active_host:
                print("=> Removing active host...")
                if len(self.available_hosts) > 0:
                    self.active_host = self.available_hosts[0]
                    print("=> Changing active host to %s" %self.active_host)
                else:
                    self.active_host = []  # reset
                    print("=> Reseting active host to []")
            self.save_hosts()
            print("=> Deleted.")
        else:
            print("=> Host does not exist, please check input with hostlist command!")
        return
    
    def switch(self, username, host, port=22):
        """Switch active host"""
        info = [username, host, port]
        if info in self.available_hosts:
            self.active_host = info
            self.save_hosts()
            print("=> Activated.")
        else:
            print("Host does not exist, please check input with hostlist command!")
        return
        
    def list(self):
        """List all remote hosts"""

        #TODO Create a pretty table for showing list
        pp = pprint.PrettyPrinter(width=40)
        print()
        print("Active host")
        print("="*12)
        print("%s" %self.active_host)
        print()
        print("Available hosts")
        print("="*15)
        pp.pprint(self.available_hosts)
        return
    
    def connect(self, privatekey_file="~/.ssh/id_rsa", passphrase=''):
        """Connect active host and open a session"""
        privatekey_file = os.path.expanduser(privatekey_file)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self.active_host[1], self.active_host[2]))
        s = Session()
        s.handshake(sock)
        try:
            # Try using private key file first
            s.userauth_publickey_fromfile(self.active_host[0], privatekey_file, passphrase)
        except:
            # Use password to auth
            passwd = input('No private key found.\nEnter your password for %s: ' %self.active_host[0])
            s.userauth_password(self.active_host[0], passwd)
        self.session = s.open_session()
        return
    
    def cmd(self, commands):
        """Run command(s) in active remote host"""
        self.connect()
        self.session.execute(commands)
        datalist = []
        try:
            # Get output
            size, data = self.session.read()
            # Here data is byte type
            while size > 0:
                data = data.decode('utf-8')
                print(data, end='')
                datalist.append(data)
                size, data = self.session.read()
        except Exception as e:
            # Get exit status
            print("Exit status: %s" % self.session.get_exit_status())
            print("Error info:\n%r" %e)
        # finally:
        #     self.session.close()
        
        # Return a list containing output from commands 
        return datalist

    def upload(self):
        """Upload files to active remote host"""
        pass
    def download(self):
        """Download files to local machine from active remote host"""
        pass


class PBS:
    """
    Representation of PBS task
    """
    def __init__(self):
        pass
    def gen_template(self):
        pass
    def gen_pbs(self):
        pass
    def sub(self):
        """Submit all pbs tasks in a remote directory"""
        pass
    def check(self):
        """Check PBS task status"""
        pass

if __name__ == "__main__":
    host = Host()
    host.add(username="wsx", host="10.19.24.165")
    host.list()
    host.cmd("ls -l")