#!/usr/bin/env python
import os
import string


def parse(path):
    with open(path) as f:
        string = f.read()
    init()
    return parseObj({}, string, 0)


def extract(statement, start_delimiter, end_delimiter):
    start_delimiter_pos = statement.find(start_delimiter)
    start = start_delimiter_pos + len(start_delimiter)
    end_delimiter_pos = statement[start:].find(end_delimiter)
    end = end_delimiter_pos + len(end_delimiter) + start - 1
    start_is_found = True if start_delimiter_pos >= 0 else False
    end_is_found = True if end_delimiter_pos >= 0 else False
    return start_is_found, end_is_found, start, end


def extractor(statement, start_delimiter, end_delimiter):
    is_processing = True
    items = []
    while is_processing:
        start_is_found, end_is_found, start, end = extract(statement, start_delimiter, end_delimiter)
        if not start_is_found:
            is_processing = False
        elif not end_is_found:
            raise Exception("End delimiter '{}' was not found".format(end_delimiter))
        else:
            items.append(statement[start:end])
            statement = statement[end + 1:]
    return items


def get_name_from_properties(properties_file, item):
    result = None
    is_searching = True
    with open(properties_file, 'r') as f:
        while is_searching:
            line = f.readline()
            if line is None:
                is_searching = False
            if line.startswith(item):
                equal_pos = line.find('=')
                if equal_pos >= 0:
                    result = line[equal_pos+1:].strip()
                    is_searching = False
                else:
                    Exception("Malformed property line: {}".format(line))
    return result


def list(path):
    include_token = 'include'
    include_token_counter = 0
    root_project_token = 'rootProject.name'
    root_project_token_counter = 0

    items = []
    with open(path, 'r') as f:
        for line in f:
            include_pos = line.find(include_token)
            if include_pos >= 0:
                start = include_pos + len(include_token)
                line = line[start:]
                items += extractor(line, "':", "'")
                include_token_counter += 1
            else:
                root_project_pos = line.find(root_project_token)
                if root_project_pos >= 0:
                    equal_pos = line.find("=")
                    if equal_pos < 0:
                        raise Exception("An equal token is expected on line: {}".format(line))
                    else:
                        item = line[equal_pos + 1:].strip()
                        if item.startswith("'"):
                            if item.endswith("'"):
                                item = item[1:-1]
                            else:
                                raise Exception("Malformed statement ' is missing: {}".format(line))
                        else:
                            properties_file = os.path.join(os.path.dirname(path), 'gradle.properties')
                            property_token = item
                            item = get_name_from_properties(properties_file, item)
                            if item is None:
                                raise Exception("Property not found '{}'".format(property_token))
                        items.append(item)
                        root_project_token_counter += 1
        if include_token_counter == 0 and root_project_token_counter == 0:
            raise Exception("Missing include or rootProject.name token")
        elif root_project_token_counter > 1:
            raise Exception("Error multiple rootProject.name token used")
    return items


def init():
    global word
    global lastWord
    global lastChar
    word = ""
    lastWord = ""
    lastChar = ""


def parseObj(root, raw, index):
    global word
    global lastWord
    global lastChar
    char = ""
    length = len(raw) - 1
    blocks = [root]
    tag = ""
    tags = [tag]
    obj = root
    i = index
    while i < length:
        i += 1
        lastChar = char
        char = raw[i]
        if char == "/" and lastChar == "/":
            i = skipToNext(raw, "\n", i)
            char = raw[i]

        if char == " " or char == "\n":
            keepWord()

        if "(" == char and tag == "repositories":
            obj[word] = ""
            keepWord()
            i = skipToNext(raw, ")", i)
            continue

        if "{" == char:
            keepWord()
            if tag == "dependencies":
                i = skipToNext(raw, "}", i)
                continue
            tags.append(tag)
            tag = lastWord

            if tag != "maven":
                blocks.append(obj)
                child = {}
                obj[tag] = child
                obj = child

        if "}" == char:
            if tag != "maven":
                obj = blocks.pop()
            tag = tags.pop()

        if tag in ["dependencies", "repositories", "maven"]:
            i = checkString(raw, char, "'", obj, i)
            i = checkString(raw, char, "\"", obj, i)
            if tag == "dependencies" and lastWord in ["group", "name", "version"]:
                mergeDependency(obj)

        if isText(char):
            word += char

    return root


def mergeDependency(obj):
    group = ""
    name = ""
    version = ""
    for key in obj:
        if obj[key] == "group":
            group = key
        elif obj[key] == "name":
            name = key
        elif obj[key] == "version":
            version = key
    if group and name and version:
        obj.pop(group, None)
        obj.pop(name, None)
        obj.pop(version, None)
        obj[group + ":" + name + ":" + version] = ""


def skipToNext(raw, target, index):
    length = len(raw)
    i = index
    while i < length and raw[i] != target:
        i += 1
    return i


def checkString(raw, char, target, obj, index):
    if target == char:
        end = skipToNext(raw, target, index + 1)
        obj[raw[index + 1:end]] = lastWord
        return end
    return index


def isText(char):
    if char in string.ascii_letters:
        return True
    elif char == ".":
        return True
    return False


def keepWord():
    global word
    global lastWord
    if word:
        lastWord = word
        word = ""
