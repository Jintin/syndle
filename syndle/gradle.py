#!/usr/bin/env python

import string


def parse(path):
    with open(path) as f:
        string = f.read()
    init()
    return parseObj({}, string, 0)


def list(path):
    with open(path) as f:
        str = f.read()
    str = str[7:]

    extra = "\"'\n :"
    for char in extra:
        str = str.replace(char, "")
    list = str.split(",")
    return list


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
