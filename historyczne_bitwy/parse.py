from lxml import html

from historyczne_bitwy.models import LubimyCzytac


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