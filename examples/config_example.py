from filip.config import Config


if __name__=='__main__':
    config = Config(path = '../config.json', loglevel="DEBUG")
    print(config)

