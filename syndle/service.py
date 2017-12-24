#!/usr/bin/python

import os
import requests


def download(url, path):
    r = requests.get(url, stream=True)
    if r.status_code == 404 or r.status_code == 401:
        return False
    if not os.path.exists(os.path.dirname(path)):
        try:
            os.makedirs(os.path.dirname(path))
        except OSError as exc:
            return False
    elif os.path.exists(path):
        return True
    handle = open(path, "wb")
    for chunk in r.iter_content(chunk_size=512):
        if chunk:  # filter out keep-alive new chunks
            handle.write(chunk)

    print("download: " + url)
    return True
