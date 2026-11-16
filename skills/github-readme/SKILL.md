---
name: github-readme
description: Write or update the README of one of the owner's GitHub repositories so a recruiter or engineer understands the project in 30 seconds and runs it in 5 minutes. Use when a repository is created, when the readme-guard hook flags a large commit, or when the owner says "readme", "opisz repo", "zaktualizuj README".
---

# README na GitHubie

Cel: czytelnik w 30 s wie, co robi projekt i co jest ciekawe w projekcie. W 5 min czytelnik uruchamia projekt.

## Kroki

Wykonaj każdy krok w tej kolejności:

1. Zbierz fakty z repo: `git log --oneline -20`, drzewo plików, manifest (`pyproject.toml`, `package.json`, `Dockerfile`), workflow CI, pliki z wynikami pomiarów. Kryterium: każde zdanie README ma źródło w repo.
2. Napisz sekcje w tej kolejności. Pomiń sekcję, której repo nie potrzebuje:
   1. tytuł i 1 zdanie: co projekt robi i dla kogo;
   2. demo: zrzut ekranu, GIF albo para wejście–wyjście;
   3. wyniki: tabela liczb z pomiaru, z datą i maszyną;
   4. szybki start: komendy od klonu do działania;
   5. sposób działania: lista kroków albo diagram;
   6. granice: czego projekt nie robi i gdzie zawodzi;
   7. licencja i autor.
3. Zastosuj każdą regułę z sekcji „Reguły ownera”.
4. Sprawdź README:
   - Uruchom każdą komendę z szybkiego startu w czystym klonie. Komendę, którą pominąłeś, oznacz w raporcie jako niesprawdzoną.
   - Otwórz każdy link.
   - Przepuść README po polsku przez `pklint`. Wynik MUSI mieć 0 naruszeń.
   - Wykonaj test README: test porównuje z kodem repo każdą liczbę README, która opisuje kod, na przykład liczbę modeli albo liczbę reguł. Test pomija liczbę z pomiaru, na przykład liczbę commitów. Wzór: plik `tests/test_readme.py` w repo `arytmetyki-generowane-funkcyjnie`.
5. Wyślij README do oceny przed commitem: tekst lidera ocenia lewa półkula. Jeżeli druga półkula nie działa, to raport podaje zdanie „bez oceny drugiej półkuli” oraz powód.
6. Zrób commit README razem ze zmianą kodu albo osobny commit `docs: ...`.

## Reguły ownera

- Ton: opis czynności. Tytuły o autorze i etykiety rangi, na przykład „flagship”, zastąp opisem tego, co projekt robi (2026-11-13).
- Autor: Maciej Szulia. Narzędzie AI MOŻE stać w sekcji technologii; README przedstawia ownera jako autora (2026-11-12).
- Język: README po angielsku dla rekrutera. Plik `README.pl.md` w PK powstaje, gdy projekt dotyczy polszczyzny albo owner o to prosi.
- Wzory: LaTeX (`$...$`, `$$...$$`) (2026-11-13).
- Diagram: tylko linie poziome i pionowe, 1 czcionka, każdy węzeł połączony (2026-09-11).
- Dane osobowe: README podaje e-mail co najwyżej w linii kontaktu; telefon, adres, nazwy firm z rekrutacji i ścieżki `/home/...` zostają poza README (2026-11-14).
- Liczby: każda liczba ma źródło i datę pomiaru. Źródło to plik wyników albo komenda.
- Tekst bez emoji (2026-08-18).

## Hook

Hook `~/.claude/hooks/readme-guard.py` działa po każdym commicie (PostToolUse na Bash). Jeżeli commit zmienia co najmniej 200 linii, dodaje katalog główny lub zmienia manifest, a README zostaje bez zmian, to hook każe uruchomić ten skill.
