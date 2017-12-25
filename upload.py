#!/usr/bin/env python

import os
import syndle

os.system("sudo rm -rf dist")
os.system("sudo python3 setup.py sdist")
os.system("twine upload dist/syndle-" + syndle.__version__ + ".tar.gz")
