import csv
import dataclasses
import hashlib
import os

import requests


@dataclasses.dataclass
class HistoryczneBitwy:
    id: int
    title: str
    date: str
    author: str
    published: list[str]
    lubimyczytac_id: int | None = None
    lubimyczytac_rating: float | None = None


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
        return file_download(url, filepath)
    else:
        return file_read(filepath)


hb_list: list[HistoryczneBitwy] = []
if not os.path.exists("./cache"):
    os.makedirs("./cache")
with open("historyczne_bitwy.csv", encoding="utf-8") as csvfile:
    hb_reader = csv.reader(csvfile, delimiter=",", quotechar='"')
    next(hb_reader)
    for row in hb_reader:
        published = []
        for p in row[4].strip().split(","):
            published.append(int(p.strip().replace("*", "")))
        hb = HistoryczneBitwy(
            id=int(row[0].strip()),
            title=row[1].strip(),
            date=row[2].strip(),
            author=row[3].strip(),
            published=published,
        )
        if hb.lubimyczytac_id is None:
            req = requests.models.PreparedRequest()
            req.prepare_url(
                "https://lubimyczytac.pl/szukaj/ksiazki", {"phrase": hb.title}
            )
            content = get_content(req.url)
            print(req.url)
            exit()
        hb_list.append(hb)
