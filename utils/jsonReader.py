import json
import os
import sys

project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_path)

class Helpers():
    def __init__(self):
        pass

    def read_json_file(self, file_name: str):
        """
        Reads the data from the file
        """

        path = f'{project_path}/{file_name}'
        try:
            with open(path) as json_file:
                data = json.load(json_file)
                return data
        except IOError:
            return None

    def update_json_file(self, file_name: str, key:str, value):
        """
        Updates the data in json file
        """
        try:
            # read data
            data = self.read_json_file(file_name)
            data[key] = value
            path = f'{project_path}/{file_name}'
            with open(path, 'w') as f:
                json.dump(data, f)
            return True
        except Exception:
            return False