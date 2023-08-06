import sshpt
import os

try:
    import unittest2 as unittest
except ImportError:
    import unittest
    
from sshpt import SSHPowerTool


class TestSSHPowerTool(unittest.TestCase):
    def test_sshpowertool(self):
        sshpt = SSHPowerTool(hosts=[127.0.0.1, ])
        sshpt.commands = "echo TEST"
        # Assign the options to more readable variables
        sshpt.username = options.username
        sshpt.password = options.password
        sshpt.keyfile = options.keyfile
        sshpt.keypass = options.keypass
        sshpt.port = options.port
        sshpt.local_filepath = options.copy_file
        sshpt.remote_filepath = options.destination
        sshpt.execute = options.execute
        sshpt.remove = options.remove
        sshpt.sudo = options.sudo
        sshpt.max_threads = options.max_threads
        sshpt.timeout = options.timeout
        sshpt.run_as = options.run_as
        sshpt.verbose = options.verbose
        sshpt.outfile = options.outfile