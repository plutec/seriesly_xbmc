import ConfigParser
import os
import sys

_config = None

def get_config(section, key):
    global _config
    if not _config:
        _config = ConfigParser.SafeConfigParser()

        project_basedir = os.path.join(os.path.dirname(__file__), 
                                       os.path.pardir)
        config_file_path = os.path.join(project_basedir, 'config.conf')
        with open(config_file_path, 'r') as f:
            _config.readfp(f)

    return _config.get(section, key)

def set_config(section, key, value, save=None):
    global _config
    if not _config:
        _config = ConfigParser.SafeConfigParser()

        project_basedir = os.path.join(os.path.dirname(__file__),
                                       os.path.pardir)
        config_file_path = os.path.join(project_basedir, 'config.conf')

        with open(config_file_path, 'r') as f:
            _config.readfp(f)

    _config.set(section, key, value)
    if save:
        fd = open(config_file_path,'w')
        _config.write(fd)
        fd.close()

def set_config_file(path):
    if not os.path.isfile(path):
        sys.stderr.write('%s is not a file. Cannot continue.' % str(path))
        sys.exit(1)

    global _config
    _config = ConfigParser.SafeConfigParser()
    _config.read(path)