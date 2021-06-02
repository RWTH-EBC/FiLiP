"""
 This an example for demonstrating the effect of different
 configuration settings. Using *.json config-files or environment
 variables. 
 Note: 
 .env-files will probably be added later.
 
 Feel free to play around with the settings and the check how 
 the urls and header parameter will be checked and/or automatically 
 guessed based on the provided information. 
 
 Imported Note:
 Although Urls are also guessed the safest is to set the service_group url directly
 """
import os


if __name__=='__main__':

    # Example using environment variables
    os.environ["ORION_URL"] = "http://localhost:1026"
    os.environ["QUANTUMLEAP_URL"] = "http://localhost:8668"
    os.environ["IOTA_URL"] = "http://localhost:4041"

    from filip import settings
    print(settings.json(indent=2))