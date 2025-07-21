import csv
from dataclasses import dataclass, fields, astuple
import hashlib
import os

import requests
from lxml import html
from unidecode import unidecode

import sqlite3


@dataclass
class Book:
    id: int
    title: str
    author: str

    @property
    def author_lastname(self) -> str:
        return self.author.split(" ")[-1]

    @property
    def author_firstname(self) -> str:
        return self.author.split(" ")[-1]

    @classmethod
    def create_query(cls) -> str:
        fields_list = []
        for f in fields(cls):
            sql_type = " "
            if f.type == int or f.type == int | None:
                sql_type += "INTEGER"
            elif f.type == float or f.type == float | None:
                sql_type += "REAL"
            elif f.type == str or f.type == list[str]:
                sql_type += "TEXT"
            fields_list.append((f.name + sql_type).strip())
        return (
            f"CREATE TABLE IF NOT EXISTS {cls.__tablename__} ({','.join(fields_list)});"
        )

    @classmethod
    def drop_query(cls) -> str:
        return f"DROP TABLE {cls.__tablename__};"


@dataclass
class HistoryczneBitwy(Book):
    __tablename__ = "historyczne_bitwy"
    date: str
    published: list[str]


@dataclass
class LubimyCzytac(Book):
    __tablename__ = "lubimy_czytac"
    rating: float
    rating_count: int
    readers: int
    reviews: int

    hb_id: int | None = None


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


def parse_content(content: bytes) -> list[LubimyCzytac]:
    result = []
    tree = html.fromstring(content.decode("utf-8"))
    book_elements = tree.xpath("//*[@id='ksiazki']/div")
    for el in book_elements:
        try:
            title = (
                el.xpath(".//*[contains(@class, 'authorAllBooks__singleTextTitle')]")[0]
                .text_content()
                .strip()
            )
            author = (
                el.xpath(".//*[contains(@class, 'authorAllBooks__singleTextAuthor')]")[
                    0
                ]
                .text_content()
                .strip()
            )
            rating = float(
                el.xpath(".//*[contains(@class, 'listLibrary__ratingStarsNumber')]")[0]
                .text_content()
                .strip()
                .replace(",", ".")
            )
            rating_count = int(
                "0"
                + el.xpath(".//*[contains(@class, 'listLibrary__ratingAll')]")[0]
                .text_content()
                .replace("ocen", "")
                .strip()
            )
            readers = int(
                "0"
                + el.xpath(".//*[contains(@class, 'mr-2')]")[-1]
                .text_content()
                .replace("Czytelnicy:", "")
                .strip()
            )
            reviews = int(
                "0"
                + el.xpath(".//*[contains(@class, 'ml-2')]")[0]
                .text_content()
                .replace("Opinie:", "")
                .strip()
            )
            href = el.xpath(
                ".//*[contains(@class, 'authorAllBooks__singleTextTitle')]"
            )[0].attrib["href"]
            lc_id = int(href.split("/")[2])
            book = LubimyCzytac(
                id=lc_id,
                title=title,
                author=author,
                rating=rating,
                rating_count=rating_count,
                readers=readers,
                reviews=reviews,
            )
            result.append(book)
        except IndexError:
            pass
    return result


hb_list: list[HistoryczneBitwy] = []
lc_list: list[LubimyCzytac] = []
if not os.path.exists("./cache"):
    os.makedirs("./cache")
with open("historyczne_bitwy.csv", encoding="utf-8") as csvfile:
    hb_reader = csv.reader(csvfile, delimiter=",", quotechar='"')
    next(hb_reader)
    dummy_match = 0
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
        req = requests.models.PreparedRequest()
        req.prepare_url(
            "https://lubimyczytac.pl/szukaj/ksiazki",
            {"phrase": hb.title + " " + hb.author.split(" ")[-1]},
        )
        search_results = parse_content(get_content(req.url))
        searched_book = None
        if search_results:
            for book in search_results:
                if unidecode(book.author_lastname) == unidecode(hb.author_lastname):
                    searched_book = book
        else:
            print(req.url)
            exit()
        if searched_book is None:
            searched_book = search_results[0]

        searched_book.hb_id = hb.id
        lc_list.append(searched_book)
        hb_list.append(hb)

database_file = "historyczne_bitwy.sqlite"
conn = sqlite3.connect(database_file)

hb_headers_create = ",".join(f.name for f in fields(HistoryczneBitwy))
hb_headers = ",".join(f.name for f in fields(HistoryczneBitwy))
hb_rows = map(astuple, hb_list)
hb_placeholders = ",".join(["?"] * len(hb_headers))
hb_table = "historyczne_bitwy"

print(HistoryczneBitwy.create_query())
print(LubimyCzytac.create_query())

# conn.executemany(query)

conn.close()
