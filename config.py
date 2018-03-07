from os.path import join, dirname, abspath
import configparser

# Config beolvasasa.
__config_file = join(dirname(abspath(__file__)), "ssh_connection.conf")
config = configparser.ConfigParser()
config.read(__config_file)
