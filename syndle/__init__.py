import syndle.gradle as gradle
import syndle.remote as remote
import os
import timeit
import sys


__version__ = "0.1"

BUILDSCRIPT = "buildscript"
PLUGINS = "plugins"
REPOSITORIES = "repositories"
ALLPROJECTS = "allprojects"
DEPENDENCIES = "dependencies"


def parse(path):
    start_time = timeit.default_timer()
    parseInner(path)
    elapsed = timeit.default_timer() - start_time
    print("total: " + str(elapsed))


def clone(package, properties, servers):
    start_time = timeit.default_timer()
    remote.parse([package], urls=servers)
    elapsed = timeit.default_timer() - start_time
    print("total: " + str(elapsed))


def load_gradle_property(file_path):
    properties = {}
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            for line in f:
                equal_pos = line.find('=')
                if equal_pos >= 0:
                    key = line[:equal_pos].strip()
                    value = line[equal_pos+1:].strip()
                    properties[key] = value
                else:
                    Exception("Malformed property line: {0}".format(line))

    return properties


def parseInner(path):
    if not path.endswith("/"):
        path += "/"
    if not os.path.exists(path):
        print("not exist path")
        return

    properties = load_gradle_property(os.path.join(path, "gradle.properties"))
    root = gradle.parse(os.path.join(path, "build.gradle"), properties)
    projects = gradle.get_projects_names(os.path.join(path, "settings.gradle"), properties)
    if BUILDSCRIPT in root:
        script = root[BUILDSCRIPT]
        print(script)
        servers = findValue(REPOSITORIES, script)
        deps = findValue(DEPENDENCIES, script)
        remote.parse(deps, urls=servers)
    elif PLUGINS in root:
        plugins = root[PLUGINS]
        print(plugins)
        # TODO

    root_servers = None
    if ALLPROJECTS in root:
        root_servers = findValue(REPOSITORIES, root[ALLPROJECTS])
    else:
        root_servers = findValue(REPOSITORIES, root)

    for p in projects:
        path_to_use = None
        if p["is_subprojects"]:
            path_to_use = os.path.join(path, p,  "build.gradle")
        else:
            path_to_use = os.path.join(path, "build.gradle")
        if os.path.exists(path_to_use):
            child = gradle.parse(path_to_use, properties)
            servers = findValue(REPOSITORIES, child)
            deps = findValue(DEPENDENCIES, child)
            if deps:
                child_servers = root_servers + servers
                remote.parse(deps, urls=child_servers)


def findValue(key, obj):
    if key in obj:
        if sys.version_info > (3, 0):
            return list(obj[key])
        else:
            return obj[key].keys()
    return []
