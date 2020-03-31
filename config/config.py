import configparser


class Config(object):
    config = configparser.ConfigParser()
    config.read('config/config.cfg')

    host = config.get('server', 'host', fallback='www.bzdnet.com')
    port = config.get('server', 'port', fallback=80)
    width = config.getint('dimension', 'width', fallback=800)
    height = config.getint('dimension', 'height', fallback=640)

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
