import filip.utils as utils

if __name__=="__main__":
    inputs = ["temperarure", "VOLC", "vav", "tür", "stuss", "fenstr", "rh",
              "id", "klappe", "druch", "CO2", "voc", "volumen", "pferd"]
    for item in inputs:
        print("input string: " + item)
        print("returned type: " + utils.create_type(item))

