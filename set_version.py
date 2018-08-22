#!/usr/bin/env python3
import json
import os

def main():
    with open('package.json', 'r+') as f:
        data = json.load(f)
        f.seek(0)
        data['version'] = os.environ['TRAVIS_TAG']
        json.dump(data, f)
        f.truncate()
