from statistics import median

from historyczne_bitwy.database import conn

for rating_count in [5, 10, 50, 100]:
    print(f"Generowanie raportu {rating_count}")
    result = conn.execute(
        f"select id,title,author,rating, rating_count from lubimy_czytac where rating_count>{rating_count} order by rating desc;"
    )
    with open(f"report_rating_{rating_count}.csv", "w", encoding="utf8") as csvfile:
        csvfile.write("Tytuł, Autor, Ocena, Ilość ocen\n")
        for row in result:
            data = [f'"{row[1]}"', f'"{row[2]}"', str(row[3]), str(row[4])]
            csvfile.write(",".join(data) + "\n")

print("Generowanie raportu średnia ocena autora")
result = conn.execute(
    "select author, round(avg(rating), 1), count(title) as ilosc_ksiazek from lubimy_czytac where rating_count>10 group by author order by avg(rating) desc;"
)
with open("report_median_rating_by_author.csv", "w", encoding="utf8") as csvfile:
    csvfile.write("Autor, Śrenida ocena, Ilość ocen\n")
    for row in result:
        data = [f'"{row[0]}"', str(row[1]), str(row[2])]
        csvfile.write(",".join(data) + "\n")


result = conn.execute("""select lc.id, lc.title, lc.author, lc.rating, hb.published from lubimy_czytac as lc
left join historyczne_bitwy as hb
on hb.id = lc.hb_id
where lc.hb_id is not NULL and lc.rating_count>10;""")
per_published_year = {}
per_first_published_year = {}
for row in result:
    if isinstance(row[4], str):
        published = row[4].split(",")
    else:
        published = [row[4]]
    # collect per_first_published_year
    if int(published[0]) in per_first_published_year:
        per_first_published_year[int(published[0])] += [row[3]]
    else:
        per_first_published_year[int(published[0])] = [row[3]]
    # collect all per_published_year
    for p in published:
        if int(p) in per_published_year:
            per_published_year[int(p)] += [row[3]]
        else:
            per_published_year[int(p)] = [row[3]]

print("Generowanie raportu średnia ocena w/g daty pierwszego wydania")
for k, v in per_first_published_year.items():
    per_first_published_year[k] = round(median(v), 2)
with open("report_per_first_published_year.csv", "w", encoding="utf8") as csvfile:
    csvfile.write("Rok pierwszego wydania, Średnia ocena\n")
    for row in sorted(per_first_published_year.items()):
        csvfile.write(",".join([str(row[0]), str(row[1])]) + "\n")

print("Generowanie raportu średnia ocena w/g daty wydania")
for k, v in per_published_year.items():
    per_published_year[k] = round(median(v), 2)
with open("report_per_published_year.csv", "w", encoding="utf8") as csvfile:
    csvfile.write("Rok wydania, Średnia ocena\n")
    for row in sorted(per_published_year.items()):
        csvfile.write(",".join([str(row[0]), str(row[1])]) + "\n")
