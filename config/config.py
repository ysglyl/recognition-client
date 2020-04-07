import configparser


class Config(object):
    config = configparser.ConfigParser()
    config.read('config/config.cfg')

    host = config.get('server', 'host', fallback='http://www.bzdnet.com')
    port = config.get('server', 'port', fallback=80)
    width = config.getint('dimension', 'width', fallback=800)
    height = config.getint('dimension', 'height', fallback=640)
    threshold_sure = config.getint('recognition', 'threshold_sure', fallback=50)
    threshold_guess = config.getint('recognition', 'threshold_guess', fallback=80)
    show_name = config.getboolean('recognition', 'show_name', fallback=True)
    show_welcome_msg = config.getboolean('recognition', 'show_welcome_msg', fallback=True)
    show_match_result = config.getboolean('recognition', 'show_match_result', fallback=True)

    @staticmethod
    def save_server(server):
        Config.config['server'] = server
        Config.host = server['host']
        Config.port = server['port']
        with open("config/config.cfg", 'w') as configure:
            Config.config.write(configure)
        return True

    @staticmethod
    def save_dimension(dimension):
        Config.config['dimension'] = dimension
        Config.width = dimension['width']
        Config.height = dimension['height']
        with open("config/config.cfg", 'w') as configure:
            Config.config.write(configure)
        return True
