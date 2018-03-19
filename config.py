from os.path import join, dirname, abspath, isfile
import configparser

# Config beolvasasa.
__config_file = join(dirname(abspath(__file__)), "ssh_connection.conf")
config = configparser.ConfigParser()
if isfile(__config_file):
	config.read(__config_file)
else:
	raise RuntimeError("Nem talaltam meg az inditashoz szukseges config fajt: ", __config_file)
