import paramiko
try:
	from .config import config
except:
	from config import config

# SSH cuccok beallitasa.
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.load_system_host_keys()
ssh.connect(
	config['nstrs2']['server'], 
	username=config['nstrs2']['username'], 
	password=config['nstrs2']['password']
)