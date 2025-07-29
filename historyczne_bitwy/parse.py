from lxml import html
from lat_lon_parser import parse
from historyczne_bitwy.models import LubimyCzytac, HistoryczneBitwy


def parse_lubimyczytac(content: bytes) -> list[LubimyCzytac]:
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


def parse_wikipedia_search(content: bytes, hb: HistoryczneBitwy) -> str | None:
    tree = html.fromstring(content.decode("utf-8"))
    search_results = tree.xpath("//*[contains(@class, 'mw-search-result-heading')]/a")
    search_for = ["bitwa", "oblężenie", "operacja", "zdobycie", "powstanie"]
    for element in search_results:
        title = element.attrib["title"]
        for s in search_for:
            if title.lower().find(s) >= 0:
                return "https://pl.wikipedia.org" + element.attrib["href"]
    for element in search_results:
        title = element.attrib["title"]
        if hb.title.lower().find(title.lower()) >= 0:
            return "https://pl.wikipedia.org" + element.attrib["href"]
    return None


def parse_wikipedia_location(content: bytes) -> tuple[float, float] | None:
    tree = html.fromstring(content.decode("utf-8"))
    result = None
    try:
        latitude = tree.xpath("//span[contains(@class,'latitude')]")[0].text
        longitude = tree.xpath("//span[contains(@class,'longitude')]")[0].text
        if latitude and longitude:
            result = (parse(latitude), parse(longitude))
    except IndexError:
        pass
    return result
