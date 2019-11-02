from ruamel.yaml import YAML


"""
    opens config file and parses yaml    
    returns a dictionary containing 
    the config settings if path exists
    otherwise an exception is thrown
"""
def load_config(path):
    with open(path) as fd: 
        yaml = YAML()
        config = yaml.load(fd)

    return dict(config)

#TODO - actually implement this ;)
"""
    make sure that config contains all of
    the fields within config_template

    handles nested dictionaries, lists and tuples
"""
def verify_config(config, config_template):
    return True

