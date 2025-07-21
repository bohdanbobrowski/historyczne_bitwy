# Historyczne bitwy

Historyczne bitwy – polska seria wydawnicza o charakterze popularnonaukowym wydawana od 1980 roku, początkowo przez wydawnictwo Ministerstwa Obrony Narodowej, a od tomu 33. (Warszawa 1656) przez Dom Wydawniczy Bellona. W serii ukazują się książki przedstawiające tło historyczne, przebieg i konsekwencje ważniejszych bitew z dziejów świata i Polski. 

## Źródła danych

1. Tabela `historyczne_bitwy.ods` i `historyczne_bitwy.csv` pobrane zostały artykułu na Wikipedii opisującej serię: https://pl.wikipedia.org/wiki/Historyczne_bitwy
2. Publicznie dostępne dane dotyczące ocen książek, ilości recenzji pochodzą z serwisu [lubimyczytac.pl](https://lubimyczytac.pl)

## Instalacja

    git clone
    cd historyczne_bitwy
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt

## Uruchamianie

### 1. Pobieranie danych

    python historyczne_bitwy.py

Aby zaoszczędzić zapytań do serwisu [lubimyczytac.pl](https://lubimyczytac.pl) lokalnie tworzony jest catalog `./cache` wewnątrz którego znajdą się surowe odpowidzi z serwisu [lubimyczytac.pl](https://lubimyczytac.pl).

Efektem działania skryptu powinien być plik `historyczne_bitwy.sqlite` o wielkości 50-100 kb.

### 2. Generowanie danych wyjściowych
    
    python generuj_raport.py

## Licencja i gwarancja

Skrypty sworzyłem na własny użytek. Każdy użytkownik korzysta z oprogramowania na własną odpowiedzialność.
