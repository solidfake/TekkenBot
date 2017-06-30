"""
Reads in simple config files
"""

class ConfigReader:
    DATA_FOLDUER = "TekkenData/"

    values = {}

    def __init__(self, filename):
        path = ConfigReader.DATA_FOLDUER + filename + ".config"
        try:
            with open(path) as f:
                lines = f.readlines()

            for line in lines:
                if '=' in line and not '#' in line:
                    split = line.split("=")
                    key = split[0].strip()
                    value = not '0' in split[1]
                    self.values[key] = value
        except:
            print("Error reading config data from " + path + ". Using default values.")

    def get_property(self, property_string, default_value):
        if property_string in self.values:
            return self.values[property_string]
        else:
            return default_value


