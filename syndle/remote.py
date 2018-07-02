import syndle.service as service
import os
from xml.dom import minidom
import re

PATH_MAVEN = os.path.expanduser("~/.m2/repository/")
URL_JCENTER = "https://jcenter.bintray.com/"
EXT_LIST = [
    ".pom",
    ".jar",
    ".aar",
    # "-javadoc.jar",
    # "-sources.jar",
]

AAR_LIST = [
    ".pom",
    ".aar"
]


def parse_dependencies(dep_line):
    pattern1 = re.compile(r"([\w\.0-9]+):([\w\.\-0-9]+):([\w\.0-9]+)")
    match1 = pattern1.match(dep_line)
    if match1:
        group = match1.group(1)
        name = match1.group(2)
        version = match1.group(3)
    else:
        raise Exception("Malformed dependencies line: {0}".format(dep_line))
    return group, name, version


def parse(packages, urls=None, tree=None):
    global servers
    global history
    if tree is None:
        tree = []
    if urls is None:
        urls = [URL_JCENTER]
    servers = formServer(urls)
    history = tree
    for dep_line in packages:
        group, name, version = parse_dependencies(dep_line)
        if version.endswith("@aar"):
            version = version.replace("@aar", "")
            dispatch(group, name, version, True)
        else:
            dispatch(group, name, version)


def dispatch(group, name, version, aar=False):
    global history
    if not version:
        print("can't parse version: " + group + "." + name)
        return
    path = formPath(group, name)
    obj = path + version + "/"
    if obj in history:
        return False
    pom = PATH_MAVEN + obj + name + "-" + version + ".pom"
    if os.path.exists(pom):
        print("exist: " + pom)
        findDependency(pom, version)
        return False
    for url in servers:
        if maven(url, path, name, version, aar):
            break
    history.append(obj)


def maven(url, obj, name, version, aar):
    count = 0
    if aar:
        list = AAR_LIST
    else:
        list = EXT_LIST
    if not download(url, obj + "maven-metadata.xml", version):
        return False
    obj += version + "/"
    title = name + "-" + version
    for ext in list:
        try:
            if download(url, obj + title + ext, version):
                findDependency(PATH_MAVEN + obj + title + ext, version)
                count += 1
            elif ext == ".pom":
                return False
            if count == 2:
                return True
        except Exception as e:
            print(e)
    return False


def download(server, path, version):
    if service.download(server + path, PATH_MAVEN + path):
        return True
    return False


def findDependency(path, rootVersion):
    if path.endswith(".pom"):
        DOMTree = minidom.parse(path)

        root = DOMTree.documentElement
        try:
            dependencies = root.getElementsByTagName("dependencies")[0]
            for dependency in dependencies.getElementsByTagName("dependency"):
                try:
                    scope = xmlValue(dependency, "scope")
                    if scope == "test":
                        continue
                except Exception:
                    pass
                group = xmlValue(dependency, "groupId")
                name = xmlValue(dependency, "artifactId")
                version = xmlValue(dependency, "version")
                type = xmlValue(dependency, "type")
                if version:
                    if version.startswith("["):
                        version = version.replace("[", "").replace("]", "")
                    if version == "${project.version}":
                        version = rootVersion
                    if "${" in version:  # TODO not support currently
                        continue
                if type == "aar":
                    dispatch(group, name, version, True)
                else:
                    dispatch(group, name, version)
        except Exception as e:
            pass


def xmlValue(obj, name):
    return obj.getElementsByTagName(name)[0].childNodes[0].data


def formServer(urls):
    list = []
    for url in urls:
        if url == "jcenter":
            list.append(URL_JCENTER)
        elif url == "google":
            list.append("https://maven.google.com/")
        elif url.startswith("http") or url.startswith("https"):
            if not url.endswith("/"):
                url += "/"
            list.append(url)
    return list


def formPath(group, name):
    return group.replace(".", "/") + "/" + name + "/"
