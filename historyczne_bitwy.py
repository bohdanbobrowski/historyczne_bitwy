import csv

import os

from unidecode import unidecode

import sqlite3

from historyczne_bitwy.download_tools import get_content
from historyczne_bitwy.parse import parse_content
from historyczne_bitwy.database import conn
from historyczne_bitwy.models import HistoryczneBitwy, LubimyCzytac


def get_historyczne_bitwy(
    file_name: str = "historyczne_bitwy.csv",
) -> set[HistoryczneBitwy]:
    hb_list: set[HistoryczneBitwy] = set()
    with open(file_name, encoding="utf-8") as csvfile:
        hb_reader = csv.reader(csvfile, delimiter=",", quotechar='"')
        next(hb_reader)
        for row in hb_reader:
            published = []
            for p in row[4].strip().split(","):
                published.append(int(p.strip().replace("*", "")))
            hb_list.add(
                HistoryczneBitwy(
                    id=int(row[0].strip()),
                    title=row[1].strip(),
                    date=row[2].strip(),
                    author=row[3].strip(),
                    published=published,
                )
            )
        return hb_list


def get_lubimyczytac(
    hb_list: set[HistoryczneBitwy], cache_dir: str = "./cache"
) -> set[LubimyCzytac]:
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)
    lc_list: set[LubimyCzytac] = set()
    for hb in hb_list:
        hb_request = hb.get_lubimy_czytac_request()
        search_results = parse_content(get_content(hb_request.url))
        searched_book = None
        if search_results:
            for book in search_results:
                if unidecode(book.author_lastname) == unidecode(hb.author_lastname):
                    searched_book = book
        else:
            print(hb_request.url)
            exit()
        if searched_book is None:
            searched_book = search_results[0]

        searched_book.hb_id = hb.id
        lc_list.add(searched_book)
    return lc_list


# Create database structure if not exists
for model in [HistoryczneBitwy, LubimyCzytac]:
    q = model.create_query()
    conn.execute(q)

# Read content from csv
hb_list = get_historyczne_bitwy()

# Download content from lubimyczytac.pl
for book_list in [hb_list, get_lubimyczytac(hb_list)]:
    cnt = 0
    for book in book_list:
        if cnt == 0:
            print(book.__tablename__)
            print("=" * 100)
        cnt += 1
        q = book.insert_query()
        try:
            conn.execute(q)
        except sqlite3.OperationalError:
            print("Database error")
            print(q)
            print(book)
        except sqlite3.IntegrityError:
            pass
    conn.commit()

conn.close()
