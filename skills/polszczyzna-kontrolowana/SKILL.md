---
name: polszczyzna-kontrolowana
description: Polszczyzna Kontrolowana (PK) — controlled Polish that leaves every sentence exactly one meaning. Use whenever you write, rewrite or audit Polish text that people will act on (instrukcje, procedury, regulaminy, wymagania, specyfikacje, umowy, raporty techniczne, komunikaty z terminem lub kwotą) and whenever the user says "napisz precyzyjnie", "jednoznacznie", "usuń niejednoznaczności", "sprawdź, czy to jest jednoznaczne", "polszczyzna kontrolowana", "napisz w PK", "sprawdź w PK" or "/pk". Not for fiction, marketing copy or casual chat, and not when PK means primary key.
---

# Polszczyzna Kontrolowana (PK) 0.1

PK to zwykły polski plus zbiór reguł. Każda reguła usuwa jedno źródło zdań, które mają więcej niż 1 znaczenie.

Polska gramatyka zostawia czytelnikowi wybór w stałych miejscach: brak rodzajników, swobodny szyk, dopełniacz, spójniki, granice przedziałów. PK zamyka każde z tych miejsc konwencją. Czytelnik, który zna konwencję, odczytuje każde zdanie w 1 sposób.

Stosuj PK do tekstu po polsku, według którego ktoś działa: instrukcja, procedura, regulamin, wymaganie, specyfikacja, umowa, raport techniczny. Nie stosuj PK do literatury, reklamy i rozmowy. Do tekstu po angielsku służy ASD-STE100.

## Tryby pracy

Ustal tryb na podstawie prośby użytkownika.

| Tryb | Prośba | Wynik |
|---|---|---|
| PISZ | „napisz instrukcję”, „napisz regulamin” | Nowy tekst w PK oraz tabela „Decyzje i braki”. |
| PRZEREDAGUJ | „przepisz precyzyjnie”, „usuń niejednoznaczności” | Tekst w PK oraz tabela „Decyzje i braki”. |
| SPRAWDŹ | „sprawdź, czy tekst jest jednoznaczny” | Tabela naruszeń. Tekst źródłowy zostaje bez zmian. |

W każdym trybie obowiązują 3 zasady.

1. **Nie zgaduj faktów.** Jeżeli brakuje liczby, granicy, wykonawcy, obiektu lub daty, to wstaw znacznik `[DO USTALENIA: czego brakuje]`. Zdanie z wymyśloną liczbą szkodzi bardziej niż zdanie nieostre, bo czytelnik ufa liczbie.
2. **Nie wybieraj znaczenia po cichu.** Jeżeli zdanie źródłowe ma 2 znaczenia, to zapisz oba znaczenia w tabeli „Decyzje i braki”. Jeżeli wybór zmienia obowiązek, kwotę, termin lub bezpieczeństwo, to wstaw znacznik zamiast wyboru. Jeżeli wybór nie zmienia żadnej z tych 4 rzeczy, to wybierz znaczenie, które zgadza się z resztą tekstu. Zapisz wybór w tabeli.
3. **Sprawdź wynik.** Po napisaniu tekstu wykonaj kroki z sekcji „Kontrola”. Policz słowa. Nie zastępuj liczenia szacunkiem.

## Słowa kluczowe wymagań

Używaj tych słów w regulaminie, wymaganiu, specyfikacji i umowie. Wzorem są słowa MUST, SHOULD i MAY z RFC 2119.

| Słowo | Znaczenie |
|---|---|
| MUSI | Wymóg bez wyjątków. |
| NIE WOLNO | Zakaz bez wyjątków. |
| POWINIEN | Zalecenie. Odstępstwo jest dozwolone tylko z ważnego powodu i po ocenie skutków. |
| NIE POWINIEN | Odradzenie. Działanie jest dozwolone tylko z ważnego powodu i po ocenie skutków. |
| MOŻE | Zezwolenie. Wykonawca sam decyduje o wykonaniu działania. |

- Pisz te słowa wielkimi literami. Odmieniaj te słowa zwyczajnie: MUSZĄ, POWINNA, MOGĄ.
- Znaczenie z tabeli ma tylko zapis wielkimi literami. W PK nie pisz tych słów małymi literami.
- Nie twórz zakazu przez negację słowa MUSI. „Nie musi” znaczy brak wymogu, a nie zakaz.
- Brak wymogu zapisz słowem MOŻE: „Operator MOŻE pominąć krok 3.”
- Możliwość zdarzenia zapisz jako warunek: „Jeżeli pompa P1 pracuje bez wody, to pompa P1 przegrzewa się.”
- Zdolność urządzenia zapisz liczbą: „Pompa P1 podaje co najwyżej 40 l/min.”
- Nie pisz „należy”, „trzeba”, „powinno się”, „wymaga się”. Te słowa ukrywają wykonawcę.
- W instrukcji krok po kroku użyj trybu rozkazującego zamiast słowa MUSI.

## Reguły

Każda reguła ma numer. Podawaj numer reguły w tabeli naruszeń i w tabeli „Decyzje i braki”.

### A. Słowa

**A1. Jeden termin, jedno znaczenie.** Nazwij jedno pojęcie jednym terminem w całym tekście. Nie używaj jednego terminu dla 2 pojęć. Czytelnik traktuje nowe słowo jako nowy obiekt.
- Źle: „Zamknij zawór. Sprawdź, czy kurek jest szczelny.”
- Dobrze: „Zamknij zawór Z1. Sprawdź, czy zawór Z1 jest szczelny.”

**A2. Nazwy obiektów.** Polski nie ma rodzajników, więc słowo „zawór” znaczy „ten zawór” albo „jakiś zawór”. Nadaj każdemu obiektowi unikalną nazwę z oznaczeniem. Dla obiektu bez nazwy podaj ilość: „każdy zawór”, „dokładnie 1 zawór”.
- Źle: „Wymień filtr.” (urządzenie ma 2 filtry)
- Dobrze: „Wymień filtr F2.”

**A3. Zaimki.** Powtórz nazwę obiektu. Nie zastępuj nazwy zaimkiem. Wyjątek stanowi zaimek „który”, który stoi bezpośrednio po rzeczowniku określanym. Jeżeli zdanie nazywa 2 osoby, to zastąp słowa „swój” i „jego” nazwą właściciela.
- Źle: „Jan powiedział Piotrowi, że jego pompa przecieka.”
- Dobrze: „Jan powiedział Piotrowi, że pompa Piotra przecieka.”

**A4. Definicje.** Używaj słowa w znaczeniu podstawowym i powszechnie przyjętym. Jeżeli zachodzi co najmniej 1 z 3 przypadków, to zdefiniuj termin przed pierwszym użyciem:
- termin ma więcej niż 1 znaczenie;
- termin nie ma mierzalnej granicy;
- termin pochodzi z języka specjalistycznego.

Wzór definicji: `[termin] oznacza [rodzaj], który [cecha odróżniająca]`. Nie używaj zdefiniowanego terminu w innym znaczeniu.

**A5. Słowa nieostre.** Zastąp słowo nieostre liczbą z jednostką albo warunkiem, który czytelnik potrafi sprawdzić. Listę słów nieostrych zawiera sekcja „Słowa zakazane”.
- Źle: „Regularnie sprawdzaj ciśnienie.”
- Dobrze: „Sprawdzaj ciśnienie co 15 min.”

**A6. Wyliczenia.** Wylicz każdy element. Nie kończ wyliczenia słowami „itp.”, „itd.”, „i inne”. Jeżeli lista zawiera tylko przykłady, to napisz przed listą: „Przykłady (lista niepełna):”.

**A7. Skróty.** Przy pierwszym użyciu napisz pełną nazwę. Skrót podaj w nawiasie po pełnej nazwie.

### B. Zdanie

**B1. Wykonawca.** Nazwij wykonawcę w każdym zdaniu o działaniu. Użyj strony czynnej. Tylko jeżeli wykonawca jest nieznany, użyj strony biernej. Konstrukcja ze słowem „się” ukrywa wykonawcę.
- Źle: „Zawór zamyka się po pracy.” (3 znaczenia: ktoś zamyka zawór; zawór zamyka się sam; czytelnik ma zamknąć zawór)
- Dobrze: „Operator zamyka zawór Z1 po zakończeniu pracy.”

**B2. Szyk.** Stosuj szyk: podmiot, orzeczenie, dopełnienie. Rzeczownik nijaki i rzeczownik męski nieżywotny mają biernik równy mianownikowi. W zdaniu z 2 takimi rzeczownikami tylko szyk wskazuje wykonawcę.
- Przykład: „Ciśnienie zmienia przepływ.” Poza PK to zdanie ma 2 znaczenia. W PK pierwszy rzeczownik jest podmiotem.

**B3. Instrukcja.** Pisz instrukcję w trybie rozkazującym. Jedno zdanie zawiera 1 polecenie. Wybierz aspekt czasownika:
- działanie jednorazowe, czasownik dokonany: „Zamknij zawór Z1.”
- działanie powtarzane, czasownik niedokonany i czas: „Sprawdzaj ciśnienie co 15 min przez 2 h.”

**B4. Czynność jako czasownik.** Nazwij czynność czasownikiem, a nie rzeczownikiem z dopełniaczem. Nie łącz więcej niż 3 rzeczowników w jeden ciąg.
- Źle: „kontrola pracownika” (2 znaczenia: pracownik kontroluje coś; ktoś kontroluje pracownika)
- Dobrze: „Kierownik kontroluje pracownika.”

**B5. Imiesłowy.** Nie używaj imiesłowów z końcówką „-ąc”, „-wszy”, „-łszy”. Napisz pełne zdanie. Imiesłów nie nazywa relacji czasu między działaniami i nie nazywa wykonawcy.
- Źle: „Otwierając zawór, obserwuj manometr.”
- Dobrze: „Otwieraj zawór Z1. W tym samym czasie obserwuj manometr M1.”

**B6. Zasięg określenia.** Postaw określenie bezpośrednio przy słowie określanym. Jeżeli określenie pasuje do 2 słów, to powtórz określenie albo podziel zdanie.
- Źle: „Wymień stare kable i przewody.” Dobrze: „Wymień stare kable i stare przewody.”
- Źle: „Kierownik powiadomił operatora o awarii w biurze.” Dobrze: „Awaria wystąpiła w biurze. Kierownik powiadomił operatora o awarii.”

**B7. Słowo „tylko”.** Postaw słowo „tylko” bezpośrednio przed słowem ograniczanym. Tę samą regułę stosuj do słów „także” i „nawet”.
- „Tylko operator otwiera zawór Z1.” (inna osoba nie otwiera zaworu Z1)
- „Operator otwiera tylko zawór Z1.” (operator nie otwiera innego zaworu)

**B8. Długość.** Instrukcja ma co najwyżej 20 słów. Opis ma co najwyżej 25 słów. Akapit ma co najwyżej 6 zdań i 1 temat. Słowo to ciąg znaków między spacjami, który zawiera co najmniej 1 literę lub cyfrę. Każde zdanie opisu ma podmiot i orzeczenie.

### C. Logika

**C1. „Lub” i „albo”.** „Lub” znaczy: co najmniej 1 człon. „Albo” znaczy: dokładnie 1 człon. Nie używaj w tej roli słów „bądź”, „czy”, „względnie”, „ewentualnie”, „i/lub” ani ukośnika.
- „Zapłać kartą lub gotówką.” (klient MOŻE użyć obu form w 1 płatności)
- „Wybierz termin A albo termin B.” (klient wybiera dokładnie 1 termin)

**C2. „I” razem z „lub”.** Nie łącz słowa „i” ze słowem „lub” ani ze słowem „albo” w 1 zdaniu. Zapis „A i B lub C” ma 2 znaczenia: „(A i B) lub C” oraz „A i (B lub C)”. Użyj listy z reguły E2.

**C3. Warunki.** Napisz warunek przed działaniem. Używaj tylko 4 wzorów:

| Wzór | Znaczenie |
|---|---|
| „Jeżeli W, to D.” | Spełniony warunek W wystarcza, żeby D obowiązywało. |
| „Gdy Z, D.” | D zaczyna się w chwili zdarzenia Z. |
| „Dopóki S, D.” | D obowiązuje przez cały czas trwania stanu S. |
| „Tylko jeżeli W, D.” | D jest dozwolone wyłącznie przy spełnionym warunku W. |

Kolejność części zdania: stan, zdarzenie, wykonawca, słowo kluczowe, działanie. Wzorem kolejności jest notacja EARS.
- Dobrze: „Dopóki pompa P1 pracuje, gdy ciśnienie p1 przekroczy 6,0 bar, sterownik MUSI wyłączyć pompę P1.”

Jeżeli przypadek przeciwny wymaga działania, to opisz przypadek przeciwny osobnym zdaniem: „Jeżeli nie W, to D2.” Nie używaj słów „jeśli”, „o ile”, „w razie”, „chyba że”, „pod warunkiem że”.

**C4. Przeczenie i „wszystkie”.** Nie łącz słów „wszyscy”, „wszystkie”, „każdy” z przeczeniem.
- Źle: „Wszystkie zawory nie są zamknięte.” (2 znaczenia)
- Dobrze: „Żaden zawór nie jest zamknięty.” albo „Co najmniej 1 zawór jest otwarty.”

**C5. Jedno przeczenie.** Pisz zdania twierdzące. Jedno zdanie zawiera co najwyżej 1 przeczenie.
- Źle: „Nie otwieraj zaworu, dopóki ciśnienie nie spadnie.”
- Dobrze: „Gdy ciśnienie p1 spadnie do wartości mniejszej niż 0,5 bar, otwórz zawór Z1.”

### D. Liczby, wielkości, czas

**D1. Wielkość.** Podaj liczbę i jednostkę. Jeżeli wartość zależy od warunków, to podaj warunki odniesienia. Zapisuj liczby cyframi. Zostaw spację między liczbą a jednostką. Oddziel części dziesiętne przecinkiem. Oddziel liczby na liście średnikiem.
- Wyjątek od spacji: symbole kąta płaskiego °, ′ i ″ stoją bezpośrednio po liczbie, np. „37,25°”.
- Źle: „Ciśnienie w instalacji: 2,5.”
- Dobrze: „Nadciśnienie w instalacji wynosi 2,5 bar przy temperaturze wody 20 °C.”

**D2. Granice i ilości.** Używaj tylko zapisów z tabeli:

| Zapis | Znaczenie |
|---|---|
| każdy | wszystkie elementy bez wyjątku |
| żaden | 0 elementów |
| dokładnie N | x = N |
| co najmniej N | x ≥ N |
| co najwyżej N | x ≤ N |
| więcej niż N | x > N |
| mniej niż N | x < N |
| od A do B włącznie | A ≤ x ≤ B |
| najwcześniej T | chwila t ≥ T |
| najpóźniej T | chwila t ≤ T |
| przed T | chwila t < T |
| po T | chwila t > T |

- Źle: „Dzieci do 3 lat wchodzą bezpłatnie.” (2 znaczenia: mniej niż 3 lata; mniej niż 4 lata)
- Dobrze: „Dziecko, które ma mniej niż 4 lata, wchodzi bezpłatnie.”

**D3. Daty i godziny.** Zapisz datę jako RRRR-MM-DD (ISO 8601) albo z nazwą miesiąca: „13 listopada 2026 r.” Zapisz godzinę w formacie 24-godzinnym GG:MM. Nie używaj słów, które zależą od dnia czytania: „dziś”, „jutro”, „w przyszłym tygodniu”.
- Źle: „Wyślij raport do piątku.”
- Dobrze: „Wyślij raport najpóźniej 2026-11-13 o godz. 16:00.”

**D4. Terminy i częstość.** Dla terminu w dniach podaj 3 dane: zdarzenie początkowe, liczbę dni, dzień numer 1. Częstość zapisz jako „co N jednostek” albo „N razy na okres”. Słowo „dzień” znaczy w PK dzień kalendarzowy. Okres 24 h nazwij słowem „doba”.
- Źle: „Złóż reklamację w ciągu 14 dni.”
- Dobrze: „Złóż reklamację najpóźniej w dniu 14. Dzień 1 to dzień po dniu odbioru towaru.”

**D5. Zmiany i porównania.** Podaj wartość przed zmianą, wartość po zmianie i jednostkę. Nie pisz „N razy mniej”. Odróżniaj procent od punktu procentowego.
- Źle: „Cena wzrosła o 25 %.”
- Dobrze: „Cena wzrosła z 40 zł do 50 zł, czyli o 10 zł (25 %).”
- Dobrze: „Stopa spadła z 4 % do 3 %, czyli o 1 punkt procentowy.”

**D6. Duże liczby i przybliżenia.** Liczbę równą co najmniej 10^9 zapisz ze skrótem „mld” albo jako potęgę liczby 10. Angielskie „billion” to 10^9, a polski „bilion” to 10^12. Do słowa „około” dodaj tolerancję: „50 m ± 5 m”.

### E. Struktura tekstu

**E1. Kroki.** Jedno polecenie zajmuje 1 zdanie i 1 krok. Jeżeli kolejność ma znaczenie, to ponumeruj kroki. Oczekiwany wynik kroku zapisz jako fakt po kroku: „Wynik: lampka L1 świeci.”

**E2. Listy.** Dla co najmniej 3 członów użyj listy pionowej. Nagłówek listy nazywa logikę:
- „Wykonaj każdy krok w tej kolejności:”
- „Spełnij każdy warunek:”
- „Spełnij co najmniej 1 warunek:”
- „Wybierz dokładnie 1 opcję:”

**E3. Ostrzeżenia.** Postaw ostrzeżenie przed krokiem, którego ostrzeżenie dotyczy. Zacznij ostrzeżenie od polecenia albo od warunku. Po poleceniu nazwij skutek.
- Dobrze: „OSTRZEŻENIE: Odłącz zasilanie przed zdjęciem pokrywy. Napięcie 230 V grozi śmiertelnym porażeniem.”

**E4. Odesłania.** Odsyłaj do numeru lub do nazwy: „patrz krok 4”, „reguła C1”. Nie pisz „powyżej”, „poniżej”, „jak wspomniano”.

**E5. Wzory.** Zapisz każdy wzór w 1 wierszu. Pod wzorem zdefiniuj każdy symbol. Podaj jednostkę każdego symbolu.

**E6. Legenda.** Konwencja działa tylko dla czytelnika, który zna konwencję. Jeżeli czytelnik nie zna PK, to dodaj legendę na początku tekstu. Legenda wymienia tylko konwencje użyte w tekście.

> Legenda: „lub” znaczy co najmniej 1 z członów. „Albo” znaczy dokładnie 1 z członów. MUSI to wymóg. NIE WOLNO to zakaz. POWINIEN to zalecenie. MOŻE to zezwolenie.

### F. Źródło informacji (moduł dla raportów)

W raporcie dodaj znacznik źródła na końcu każdego zdania o fakcie. Znacznik mówi czytelnikowi, skąd autor zna fakt.

| Znacznik | Znaczenie |
|---|---|
| `[pomiar: przyrząd, data, godzina]` | Autor zmierzył wartość. |
| `[obserwacja: data, godzina]` | Autor widział zdarzenie lub stan. |
| `[obliczenie: dane wejściowe]` | Autor obliczył wartość. |
| `[źródło: dokument, strona]` | Autor przepisał informację z dokumentu. |
| `[relacja: osoba, data]` | Inna osoba przekazała informację autorowi. |
| `[założenie]` | Autor przyjął informację bez sprawdzenia. |

Nie używaj słów „podobno”, „chyba”, „raczej”, „prawdopodobnie”. Użyj znacznika.
- Dobrze: „Nadciśnienie w instalacji wynosi 2,5 bar `[pomiar: manometr M1, 2026-11-10, 14:30]`.”

## Słowa zakazane

| Nie pisz | Powód | Napisz |
|---|---|---|
| odpowiedni, właściwy, stosowny, należyty | brak kryterium | warunek, który czytelnik potrafi sprawdzić |
| niezwłocznie, wkrótce, szybko, na bieżąco | brak czasu | „w czasie krótszym niż N” albo data z godziną |
| regularnie, okresowo, często, rzadko, zwykle | brak częstości | „co N jednostek” |
| kilka, kilkanaście, parę, wiele, większość | brak liczby („kilkanaście” obejmuje wartości od 11 do 19) | liczba |
| duży, mały, wysoki, niski, długi, krótki | brak miary | liczba z jednostką |
| około, mniej więcej, prawie | brak tolerancji | wartość ± tolerancja |
| do, powyżej, poniżej, ponad, między, minimum, maksimum (jako granica) | granica włączona albo wyłączona | zapis z reguły D2 |
| dziś, jutro, wczoraj, obecnie, ostatnio, następny, przyszły, zeszły | znaczenie zależy od dnia czytania | data |
| ostatni | 2 znaczenia: końcowy; najnowszy | „końcowy” albo nazwa z datą |
| bądź, czy (jako spójnik), względnie, ewentualnie, i/lub, ukośnik | 2 znaczenia | „lub” albo „albo” |
| jeśli, o ile, w razie, chyba że, pod warunkiem że | więcej niż 1 słowo dla 1 relacji | wzór z reguły C3 |
| należy, trzeba, powinno się, wymaga się | brak wykonawcy | wykonawca i słowo kluczowe |
| musi, powinien, może (małymi literami) | 2 znaczenia | słowo kluczowe albo warunek |
| itp., itd., i inne, m.in. | lista otwarta | pełna lista albo „Przykłady (lista niepełna):” |
| dowolny, niektóre, pewien, jakiś | brak ilości | „każdy”, „dokładnie 1”, „co najmniej 1” |
| podobno, chyba, raczej, prawdopodobnie | brak źródła | znacznik z modułu F |
| on, ona, go, jej, jego, ich, swój, ten, to (zamiast nazwy) | odniesienie do 2 obiektów | nazwa obiektu |
| imiesłów z końcówką -ąc, -wszy, -łszy | ukryta relacja czasu | pełne zdanie |

## Słownik terminów PK

| Termin | Definicja |
|---|---|
| człon | Część zdania połączona z inną częścią spójnikiem „i”, „lub” albo „albo”. |
| wykonawca | Osoba lub urządzenie, które wykonuje działanie. |
| obiekt | Rzecz, o której mówi zdanie. |
| termin | Słowo lub wyrażenie, które ma w tekście 1 zdefiniowane znaczenie. |
| znaczenie | Jeden sposób odczytania zdania. |
| instrukcja | Zdanie, które każe czytelnikowi wykonać działanie. |
| opis | Zdanie, które stwierdza fakt lub wymóg. |
| słowo nieostre | Słowo bez mierzalnej granicy. |

Jeżeli tekst ma co najmniej 3 terminy, to dodaj przed treścią sekcję „Słownik”. Sekcja „Słownik” ma 3 kolumny: termin, definicja, słowa zakazane dla tego pojęcia.

## Kontrola

Po napisaniu tekstu wykonaj każdy krok w tej kolejności:

1. Policz słowa w każdym zdaniu. Popraw każde zdanie, które przekracza limit z reguły B8.
2. Wyszukaj w tekście każde słowo z sekcji „Słowa zakazane”.
3. Wskaż wykonawcę w każdym zdaniu o działaniu.
4. Sprawdź każdą liczbę: jednostka, warunki odniesienia, zapis granicy z reguły D2.
5. Sprawdź każdą datę i każdą godzinę: format z reguły D3.
6. Sprawdź każdy termin: 1 nazwa w całym tekście i definicja w sekcji „Słownik”.
7. Wykonaj test 2 znaczeń. Dla każdego zdania poszukaj drugiego znaczenia. Przeredaguj każde zdanie, które ma drugie znaczenie.

Jeżeli masz narzędzie do uruchamiania kodu, to policz słowa skryptem. Liczenie w pamięci daje błędy.

```python
import re, sys

for line in sys.stdin:
    for s in re.split(r"(?<=[.!?])\s+", line.strip()):
        n = sum(1 for w in s.split() if re.search(r"\w", w))
        if n > 20:
            print(n, s)
```

Skrypt wypisuje każde zdanie, które ma więcej niż 20 słów. Opis, który ma od 21 do 25 słów włącznie, spełnia regułę B8. Skrót z kropką dzieli zdanie w złym miejscu. Zdanie ze skrótem policz ręcznie.

## Format wyniku

Tryb PISZ i tryb PRZEREDAGUJ zwracają 3 części w tej kolejności:

1. Sekcja „Słownik”. Jeżeli tekst ma mniej niż 3 terminy, to pomiń sekcję „Słownik”.
2. Tekst w PK.
3. Tabela „Decyzje i braki” z kolumnami: Nr, Fragment, Reguła, Znaczenia lub brak, Wybór.

Tryb SPRAWDŹ zwraca tabelę naruszeń z kolumnami: Nr, Fragment, Reguła, Problem, Poprawka. W kolumnie „Problem” zapisz oba znaczenia fragmentu. Pod tabelą podaj liczbę naruszeń dla każdej reguły.

## Przykład

Kontekst od użytkownika: urządzenie ma 1 zawór (Z1) i 1 filtr (F1).

Tekst źródłowy: „Po pracy należy zamknąć zawór. Filtr trzeba regularnie czyścić. Protokół wysłać do piątku.”

Tekst w PK:

- Po zakończeniu pracy zamknij zawór Z1.
- Czyść filtr F1 co `[DO USTALENIA: odstęp między czyszczeniami]`.
- Wyślij protokół do `[DO USTALENIA: odbiorca]` najpóźniej `[DO USTALENIA: data i godzina]`.

Decyzje i braki:

| Nr | Fragment | Reguła | Znaczenia lub brak | Wybór |
|---|---|---|---|---|
| 1 | „należy”, „trzeba”, „wysłać” | B1 | Brak wykonawcy. | Wykonawcą jest czytelnik instrukcji. Tryb rozkazujący. |
| 2 | „regularnie” | A5 | Brak częstości. | `[DO USTALENIA]` |
| 3 | „do piątku” | D2, D3 | 2 znaczenia: termin obejmuje piątek; termin kończy się przed piątkiem. Brak daty. | `[DO USTALENIA]` |
| 4 | „wysłać” | B1 | Brak odbiorcy. | `[DO USTALENIA]` |

## Granice standardu

- PK nie zmienia ortografii ani interpunkcji. Obowiązują „Zasady pisowni i interpunkcji polskiej” Rady Języka Polskiego, ważne od 2026-01-01.
- Cytat, nazwa własna i napis z interfejsu zostają bez zmian. Zapisz taki fragment w cudzysłowie.
- Polecenie użytkownika ma pierwszeństwo przed regułą PK. Zapisz odstępstwo w tabeli „Decyzje i braki”.
- Jeżeli 2 reguły kolidują, to jednoznaczność wygrywa z długością. Podziel zdanie.
- Umowa w PK nadal wymaga oceny prawnika. PK usuwa niejednoznaczność języka i nie ocenia skutków prawnych.
- PK to inny standard niż prosty język. Prosty język służy łatwemu zrozumieniu (ISO 24495-1). PK służy jednemu znaczeniu. Autor MOŻE zastosować oba standardy w 1 tekście.

## Źródła

- Słowa kluczowe: [RFC 2119](https://www.rfc-editor.org/rfc/rfc2119) (S. Bradner, 1997) oraz [RFC 8174](https://www.rfc-editor.org/info/rfc8174).
- A1, A4, A6, A7, B5, B8: [„Zasady techniki prawodawczej”, Dz.U. 2026 poz. 300](https://api.sejm.gov.pl/eli/acts/DU/2026/300/text.pdf), § 7, § 8, § 10, § 146, § 147, § 151, § 153, § 154.
- B2: Zintegrowana Platforma Edukacyjna (ZPE), [„Przemiany w deklinacji polskiej: rzeczownik rodzaju męskiego”](https://zpe.gov.pl/pdf/Pkz7BO1mo) (rzeczownik męski nieżywotny ma biernik równy mianownikowi).
- B1, B3, B4, B8, E3: wzorem jest [ASD-STE100 Simplified Technical English](https://www.asd-ste100.org/), Issue 9 (2025).
- B5: [„Kilka uwag o poprawności użycia imiesłowów współczesnych”](https://polonica.ijppan.pl/index.php/polonica/article/view/782/356), „Polonica”.
- B6: ZPE, [„Kurs logiki: lekcja 15. Wieloznaczność, chwiejność składniowa i myślenie figuralne”](https://zpe.gov.pl/a/przeczytaj/DbAw1OFW1) (amfibolia).
- C1: [„Elementy logiki i teorii mnogości”](https://wydawnictwo.p.lodz.pl/images/spisy-tresci/3-30JdrzejewskaEKotlicka_wstp.pdf), Wydawnictwo Politechniki Łódzkiej; A. Kiklewicz, [„O pewnym typie użycia spójników rozłącznych w języku polskim”](https://www.press.uni.lodz.pl/index.php/wul/en/catalog/download/1334/7902/5032?inline=1).
- C3: A. Mavin i in., [Easy Approach to Requirements Syntax (EARS)](https://alistairmavin.com/ears/), 2009.
- C4: S. Przybyszewski, [„O użyciu operatorów kwantyfikacji ogólnej w zdaniach przeczących”](https://www.ceeol.com/search/article-detail?id=906854), „Język Polski” 2020, z. 3.
- D1: [rozporządzenie w sprawie legalnych jednostek miar, Dz.U. 2020 poz. 1024](https://api.sejm.gov.pl/eli/acts/DU/2020/1024/text.html), § 15; Główny Urząd Miar, [zasady pisowni SI](https://www.gum.gov.pl/ftp/jpg/Redefinicja_SI/Ulotka_SI_-_druk_2023_10_26_ost.pdf).
- D3: [ISO 8601](https://www.iso.org/iso-8601-date-and-time-format.html).
- D5: ZPE, [„Punkt procentowy”](https://zpe.gov.pl/a/przeczytaj/DsTOOMs1P).
- D6: J. Klimeczko, [„Notacja wykładnicza i jej zastosowanie w praktyce”](https://zasobyip2.ore.edu.pl/pl/publications/download/13502), zasoby Ośrodka Rozwoju Edukacji (polski „bilion”); MathWorld, [„Billion”](https://mathworld.wolfram.com/Billion.html) (angielskie „billion”).
- Słowo „kilkanaście”: D. Roszko, R. Roszko, [„Slavia Meridionalis” 2023](https://doaj.org/article/0e38245a8c444cdbad36fa24847dc128).
- Ortografia: Ministerstwo Nauki i Szkolnictwa Wyższego, [nowe zasady pisowni](https://www.gov.pl/web/nauka/nowe-zasady-pisowni--prostsza-bardziej-spojna-ortografia).
- Prosty język: [ISO 24495-1:2023](https://www.iplfederation.org/iso-standard/).
