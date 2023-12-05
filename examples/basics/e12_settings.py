"""
# This an example for demonstrating the effect of different
# configuration settings. Using *.json config-files or environment
# variables. You can also use the .env.filip file to provide the variables
#
# Feel free to play around with the settings and the check how
# the urls and header parameter will be checked and/or automatically
# guessed based on the provided information.
 
# Note: Although Urls are also guessed the safest is to set the service url
# directly
 """
import os







if __name__ == '__main__':

    # # 1 Example using environment variables

    os.environ["ORION_URL"] = "http://localhost:1026"
    os.environ["QUANTUMLEAP_URL"] = "http://localhost:8668"
    os.environ["IOTA_URL"] = "http://localhost:4041"

    from filip import settings
    print(settings.json(indent=2))