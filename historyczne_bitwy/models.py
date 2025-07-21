from dataclasses import dataclass, fields

import requests


@dataclass
class Book:
    id: int
    title: str
    author: str

    def __getitem__(self, item):
        return getattr(self, item)

    @property
    def author_lastname(self) -> str:
        return self.author.split(" ")[-1]

    @property
    def author_firstname(self) -> str:
        return self.author.split(" ")[-1]

    @classmethod
    def create_query(cls) -> str:
        fields_list = []
        first_column = " PRIMARY KEY"
        for f in fields(cls):
            sql_type = " "
            if f.type is int or f.type == int | None:
                sql_type += "INTEGER" + first_column
            elif f.type is float or f.type == float | None:
                sql_type += "REAL" + first_column
            elif f.type is str or f.type is list:
                sql_type += "TEXT" + first_column
            fields_list.append((f.name + sql_type).strip())
            first_column = ""
        return (
            f"CREATE TABLE IF NOT EXISTS {cls.__tablename__} ({','.join(fields_list)});"
        )

    @classmethod
    def drop_query(cls) -> str:
        return f"DROP TABLE {cls.__tablename__};"

    def insert_query(self) -> str:
        values_list = []
        for f in fields(self):
            if (
                f.type is int
                or f.type == int | None
                or f.type is float
                or f.type == float | None
            ):
                values_list.append(str(self[f.name]))
            elif f.type is str:
                values_list.append(f"'{self[f.name]}'")
            elif f.name == "published":  # This is STUPID
                values_list.append(f"'{','.join(str(f) for f in self[f.name])}'")
        return f"INSERT INTO {self.__tablename__} ({','.join(field.name for field in fields(self))}) VALUES ({','.join(values_list)});"


@dataclass
class HistoryczneBitwy(Book):
    __tablename__ = "historyczne_bitwy"
    date: str
    published: list[str]

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return self.id == other.id

    def get_lubimy_czytac_request(self) -> requests.models.PreparedRequest:
        req = requests.models.PreparedRequest()
        req.prepare_url(
            "https://lubimyczytac.pl/szukaj/ksiazki",
            {"phrase": self.title + " " + self.author.split(" ")[-1]},
        )
        return req


@dataclass
class LubimyCzytac(Book):
    __tablename__ = "lubimy_czytac"
    rating: float
    rating_count: int
    readers: int
    reviews: int

    hb_id: int | None = None

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return self.id == other.id
