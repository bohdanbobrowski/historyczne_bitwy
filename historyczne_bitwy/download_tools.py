
import hashlib
import os

import requests



def get_urlhash(url):
    m = hashlib.md5()
    m.update(url.encode("utf-8"))
    return m.hexdigest()


def file_read(filepath: str) -> bytes:
    with open(filepath, "rb") as html_file:
        contents = html_file.read()
    return contents


def file_write(contents: bytes, filepath: str):
    with open(filepath, "wb") as f:
        f.write(contents)


def file_download(url: str, filepath: str) -> bytes | None:
    try:
        response = requests.get(url)
    except requests.exceptions.ConnectionError:
        return None
    file_write(response.content, filepath)
    return response.content


def get_content(url) -> bytes | None:
    filepath = f"./cache/{get_urlhash(url)}.html"
    if not os.path.isfile(filepath):
        # exit("DEBUG")
        return file_download(url, filepath)
    else:
        return file_read(filepath)
