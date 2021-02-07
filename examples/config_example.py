from filip.config import Config
import os

'''
 This an example for demonstrating the effect of different
 configuration settings. Using *.json config-files or environment
 variables. 
 Note: 
 .env-files will probably be added later.
 
 Feel free to play around with the settings and the check how 
 the urls and header parameter will be checked and/or automatically 
 guessed based on the provided information. 
 
 Imported Note:
 Although Urls are also guessed the safest is to set the service url directly
 
'''

if __name__=='__main__':
    # Example using *.json-config-file
    #config = Config(path = '../config.json', loglevel="DEBUG")
    #print(config)

    # Example using environment variables
    os.environ["CONFIG_FILE"] = "False"
    os.environ["ORION_URL"] = "http://localhost:1026"
    os.environ["QUANTUMLEAP_HOST"] = "localhost"
    os.environ["QUANTUMLEAP_PORT"] = "8668"
    os.environ["IOTA_HOST"] = "http://localhost"
    os.environ["IOTA_PROTOCOL"] = "IoTA-JSON"

    config = Config()
    print(config)