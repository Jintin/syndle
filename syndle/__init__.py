#!/usr/bin/env python

import syndle.gradle as gradle
import syndle.remote as remote
import os
import timeit
import sys


__version__ = "0.1"

BUILDSCRIPT = "buildscript"
REPOSITORIES = "repositories"
ALLPROJECTS = "allprojects"
DEPENDENCIES = "dependencies"


def parse(path):
    start_time = timeit.default_timer()
    parseInner(path)
    elapsed = timeit.default_timer() - start_time
    print("total: " + str(elapsed))


def clone(package, servers):
    start_time = timeit.default_timer()
    remote.parse([package], servers)
    elapsed = timeit.default_timer() - start_time
    print("total: " + str(elapsed))


def parseInner(path):
    if not path.endswith("/"):
        path += "/"
    if not os.path.exists(path):
        print("not exist path")
        return

    projects = gradle.list(path + "settings.gradle")
    root = gradle.parse(path + "build.gradle")

    if BUILDSCRIPT in root:
        script = root[BUILDSCRIPT]
        print(script)
        servers = findValue(REPOSITORIES, script)
        deps = findValue(DEPENDENCIES, script)
        if deps:
            remote.parse(deps, servers)

    if ALLPROJECTS in root:
        rootServers = findValue(REPOSITORIES, root[ALLPROJECTS])

    for p in projects:
        child = gradle.parse(path + "/" + p + "/build.gradle")
        servers = findValue(REPOSITORIES, child)
        deps = findValue(DEPENDENCIES, child)
        if deps:
            remote.parse(deps, rootServers + servers)


def findValue(key, obj):
    if key in obj:
        if (sys.version_info > (3, 0)):
            return list(obj[key])
        else:
            return obj[key].keys()
    return []
