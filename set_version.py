#!/usr/bin/env python3
"""Set the version in NPM's package.json to match the git tag."""
import json
import os

if __name__ == '__main__':
    with open('package.json', 'r+') as f:
        data = json.load(f)
        f.seek(0)
        data['version'] = os.environ['TRAVIS_TAG']
        json.dump(data, f)
        f.truncate()
