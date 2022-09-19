#!/usr/bin/python3

import yaml


class Config:
    def __init__(self, config_file):
        self.file = config_file
        with open(self.file, 'r') as stream:
            try:
                self.c = yaml.load(stream, Loader=yaml.SafeLoader)

            except yaml.YAMLError as exc:
                print(exc)

    def getConfig(self):
        return self.c
