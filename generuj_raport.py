from historyczne_bitwy.database import conn

for rating_count in [10, 50, 100]:
    print(f"Generowanie raportu {rating_count}")
    result = conn.execute(
        f"select id,title,author,rating, rating_count from lubimy_czytac where rating_count>{rating_count} order by rating desc;"
    )
    with open(f"raport_rating_{rating_count}.csv", "w", encoding="utf8") as csvfile:
        csvfile.write("Tytuł, Autor, Ocena, Ilość ocen\n")
        for row in result:
            data = [f'"{row[1]}"', str(row[2]), str(row[3]), str(row[4])]
            csvfile.write(",".join(data) + "\n")
