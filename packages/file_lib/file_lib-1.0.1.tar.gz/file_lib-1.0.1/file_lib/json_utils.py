# -*- coding: utf-8 -*-
import simplejson


def read_json_file(file_path):
    with open(file_path) as json:
        return simplejson.load(json)


def write_json_file(file_path, data):
    with open(file_path, 'w') as f:
        simplejson.dump(data, f, sort_keys=True, indent=4)
