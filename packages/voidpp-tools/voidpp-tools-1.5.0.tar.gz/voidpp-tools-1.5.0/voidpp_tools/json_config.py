
import os
import json

from .json_encoder import JsonEncoder

class ConfigLoaderException(Exception):
    pass

class JSONConfigLoader():
    def __init__(self, base_path, encoder = JsonEncoder):
        self.sources = [
            os.path.dirname(os.getcwd()),
            os.path.dirname(os.path.abspath(base_path)),
            os.path.expanduser('~'),
            '/etc',
        ]
        self.__loaded_config_file = None
        self.__encoder = encoder

    @property
    def filename(self):
        return self.__loaded_config_file

    def load(self, filename, create = None, default_conf = {}):
        tries = []
        for source in self.sources:
            file_path = os.path.join(source, filename)
            tries.append(file_path)
            if not os.path.exists(file_path):
                continue
            self.__loaded_config_file = file_path
            with open(file_path) as f:
                return json.load(f)

        if create is not None:
            self.__loaded_config_file = os.path.join(create, filename)
            self.save(default_conf)
            return default_conf

        raise ConfigLoaderException("Config file not found in: %s" % tries)

    def save(self, config):
        if self.__loaded_config_file is None:
            raise ConfigLoaderException("Load not called yet!")

        data = None
        try:
            data = json.dumps(config, cls = self.__encoder)
        except Exception as e:
            raise ConfigLoaderException("Config data is not JSON serializable: %s" % e)
            return

        with open(self.__loaded_config_file, 'w') as f:
            f.write(data)
