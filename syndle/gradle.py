import re

block_start = re.compile(r"\s*(\w+)\s*\{")
block_end = re.compile(r"\s*\}")
official_repo = re.compile(r"\s*(\w+)\(\)")
custom_repo = re.compile(r"\s*maven\s*\{")
dep_format1 = re.compile(
    r"\s*(classpath|test\w*|compile\w*)\s+group\s*:\s*'([\w\.]+)'\s*,\s*name\s*:\s*'([\w\.\-]+)'\s*,\s*version:\s*('?[\w\.0-9]+'?)")
dep_format2 = re.compile(r"\s*(classpath|test\w*|compile\w*)\s+'([\w\.]+):([\w\.\-]+):([\w\.0-9]+)")


def parse(path, properties):
    root = {}
    is_processing = True
    with open(path) as f:
        data = None
        is_processing = True
        is_eof = False
        while is_processing:
            if is_eof:
                is_processing = False
            else:
                line = f.readline()
                if not line:
                    is_processing = False
                    is_eof = True
                else:
                    match_start = block_start.match(line)
                    if match_start:
                        child_block_name = match_start.group(1)
                        data = {}
                        root[child_block_name], is_eof = parse_block(f, properties, child_block_name, data)
    return root


def parse_block(file_handler, properties, block_name, block):
    is_processing = True
    is_eof = False
    while is_processing:
        if is_eof:
            is_processing = False
        else:
            line = file_handler.readline()
            if not line:
                is_processing = False
                is_eof = True
            else:
                match_end = block_end.match(line)
                if match_end:
                    is_processing = False
                else:
                    match_start = block_start.match(line)
                    if match_start and match_start.group(1) != "maven":
                        child_block_name = match_start.group(1)
                        data = {}
                        block[child_block_name], is_eof = parse_block(file_handler, properties, child_block_name, data)
                    else:
                        if block_name == "repositories":
                            match_official_repo = official_repo.match(line)
                            if match_official_repo:
                                repo_name = match_official_repo.group(1)
                                block[repo_name] = ""
                                del repo_name
                            else:
                                match_custom_repo = custom_repo.match(line)
                                if match_custom_repo:
                                    # FIXME
                                    tokens = file_handler.readline().strip().split()
                                    _ = file_handler.readline()
                                    start_is_found, end_is_found, start, end = extract(tokens[1], "'", "'")
                                    repo_name = tokens[1][start:end]
                                    block[repo_name] = ""
                                    del repo_name
                                else:
                                    raise Exception("Malformed line '{0}'".format(line))
                        elif block_name == "dependencies":
                            matcher = None
                            match_dep_format1 = dep_format1.match(line)
                            if match_dep_format1:
                                matcher = match_dep_format1
                                if matcher.group(4).startswith("'"):
                                    if matcher.group(4).endswith("'"):
                                        version = matcher.group(4)[1:-1]
                                    else:
                                        raise Exception("Malformed dependencies line: '{0}'".format(line))
                                else:
                                    version_key = matcher.group(4)
                                    version = properties.get(version_key, "")
                                group = matcher.group(2)
                                name = matcher.group(3)
                                block[group + ":" + name + ":" + version] = ""
                            else:
                                match_dep_format2 = dep_format2.match(line)
                                if match_dep_format2:
                                    matcher = match_dep_format2
                                    version = matcher.group(4)
                                    group = matcher.group(2)
                                    name = matcher.group(3)
                                    block[group + ":" + name + ":" + version] = ""
                                # else:
                                #     raise Exception("Malformed line: '{0}'".format(line))
    return block, is_eof


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
            raise Exception("End delimiter '{0}' was not found".format(end_delimiter))
        else:
            items.append(statement[start:end])
            statement = statement[end + 1:]
    return items


def get_projects_names(path, properties=None):
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
                sub_projects = extractor(line, "':", "'")
                items += map(lambda x: {"name": x, "is_subprojects": True}, sub_projects)
                include_token_counter += 1
            else:
                root_project_pos = line.find(root_project_token)
                if root_project_pos >= 0:
                    equal_pos = line.find("=")
                    if equal_pos < 0:
                        raise Exception("An equal token is expected on line: {0}".format(line))
                    else:
                        item = line[equal_pos + 1:].strip()
                        if item.startswith("'"):
                            if item.endswith("'"):
                                item = item[1:-1]
                            else:
                                raise Exception("Malformed statement ' is missing: {0}".format(line))
                        else:
                            property_token = item
                            if properties is None:
                                raise Exception(
                                    "Could not evaluate the property {0} without properties dictionary".format(
                                        property_token))
                            item = properties.get(property_token, None)
                            if item is None:
                                raise Exception("Property not found '{0}'".format(property_token))
                        items.append({"name": item, "is_subprojects": False})
                        root_project_token_counter += 1
        if include_token_counter == 0 and root_project_token_counter == 0:
            raise Exception("Missing include or rootProject.name token")
        elif root_project_token_counter > 1:
            raise Exception("Error multiple rootProject.name token used")
    return items
