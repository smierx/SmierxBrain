import configparser

def get_config():
    config = configparser.ConfigParser()
    config.read("../.env")
    return config