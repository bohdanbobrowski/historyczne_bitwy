import csv


from historyczne_bitwy.download_tools import get_content
from historyczne_bitwy.parse import parse_wikipedia_search, parse_wikipedia_location
from historyczne_bitwy.models import HistoryczneBitwy


def save_historyczne_bitwy_csv(
    hb_list=set[HistoryczneBitwy],
    file_name: str = "historyczne_bitwy_wikipedia.csv",
):
    with open(file_name, "w", encoding="utf-8") as csvfile:
        csvfile.write(
            'Nr,Tytuł ,"Rok bitwy, kampanii lub wojny",Autor,Wydanie,Wikipedia_url,Lat,Lng\n'
        )
        for hb in hb_list:
            if hb.wikipedia_url is not None and hb.location is not None:
                csvfile.write(
                    f'{hb.id},"{hb.title}",{hb.date},"{hb.author}",\"{",".join(str(p) for p in hb.published)}\",{hb.wikipedia_url},{hb.location[0]},{hb.location[1]}\n'
                )
            else:
                csvfile.write(
                    f'{hb.id},"{hb.title}",{hb.date},"{hb.author}",\"{",".join(str(p) for p in hb.published)}\",???,,\n'
                )


def get_historyczne_bitwy(
    file_name: str = "historyczne_bitwy_wikipedia.csv",
) -> set[HistoryczneBitwy]:
    hb_list: set[HistoryczneBitwy] = set()
    with open(file_name, encoding="utf-8") as csvfile:
        hb_reader = csv.reader(csvfile, delimiter=",", quotechar='"')
        next(hb_reader)
        for row in hb_reader:
            published = []
            loc = None
            wikipedia_url = None
            for p in row[4].strip().split(","):
                published.append(int(p.strip().replace("*", "")))
            if row[6].strip() and row[7].strip():
                loc = (float(row[6].strip()), float(row[7].strip()))
            if row[5].strip() != "???":
                wikipedia_url = row[5].strip()
            hb_list.add(
                HistoryczneBitwy(
                    id=int(row[0].strip()),
                    title=row[1].strip(),
                    date=row[2].strip(),
                    author=row[3].strip(),
                    published=published,
                    wikipedia_url=wikipedia_url,
                    location=loc,
                )
            )
        return hb_list


# Read content from csv
hb_list = get_historyczne_bitwy()

for hb in hb_list:
    if hb.wikipedia_url is None:
        hb_request = hb.get_wikipedia_request()
        wikipedia_url = parse_wikipedia_search(get_content(hb_request.url), hb)
        if wikipedia_url is not None:
            location = parse_wikipedia_location(get_content(wikipedia_url))
            if location is not None:
                hb.wikipedia_url = wikipedia_url
                hb.location = location
    elif hb.location is None:
        hb.location = parse_wikipedia_location(get_content(hb.wikipedia_url))
    print(hb.title, hb.wikipedia_url, hb.location)
save_historyczne_bitwy_csv(hb_list)