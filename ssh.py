from os.path import join, dirname, abspath
import paramiko
import configparser

# Config beolvasasa.
__config_file = join(dirname(abspath(__file__)), "ssh_connection.conf")
config = configparser.ConfigParser()
config.read(__config_file)

# SSH cuccok beallitasa.
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.load_system_host_keys()
ssh.connect(
	config['nstrs2']['server'], 
	username=config['nstrs2']['username'], 
	password=config['nstrs2']['password']
)