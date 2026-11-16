---
name: boldness-brains
description: Place the owner's current work on the boldness-to-brains plane and suggest the next move up (a closing action) before more tooling. Use when the owner asks "gdzie jestem na wykresie", "jak się poruszać", "co domknąć", at the morning review, and when the session-start hook reports open closings.
---

# Płaszczyzna śmiałość–rozum

Polecenie ownera z 2026-11-16, 13:11: „zrób z tego skilla i hooka aby mi sugerował jak się poruszać na tej płaszczyźnie”.

Płaszczyzna pochodzi z wykresu „The boldness-to-brains ratio”. Oś pozioma to rozum, a oś pionowa to śmiałość. Strefa „Founder / empire builder” leży nad przekątną, w prawym górnym rogu wykresu. Legenda wykresu daje tej strefie poziom „High” potencjału tworzenia majątku. Punkt ownera z 2026-11-16: rozum 78 %, śmiałość 62 % (ocena agenta, nie pomiar). Punkt leży pod przekątną, więc owner zyskuje na ruchu w górę.

## Słownik

| Termin | Definicja | Nie pisz |
|---|---|---|
| domknięcie | Działanie, które kończy sprawę na zewnątrz: wysyłka, kliknięcie, podpis, odpowiedź, decyzja, sprzedaż. Domknięcie to ruch w górę. | „zamknięcie”, „finalizacja” |
| narzędzie | Skill, hook, opis, reguła albo refaktoryzacja. Narzędzie to ruch w prawo albo brak ruchu. | „usprawnienie” |
| otwarte domknięcie | Domknięcie, które czeka na ownera. | „zaległość” |

## Kroki

Wykonaj każdy krok w tej kolejności:

1. Policz otwarte domknięcia z każdego źródła:
   - rejestry zgłoszeń `portal-submissions.jsonl` w repo `~/Documents/cv-it`: karta, która ma wiersz ze stanem `filled-awaiting-owner` i nie ma późniejszego wiersza ze stanem `submitted`;
   - plik `orders/orders.json` w repo `second-brain`: składnik rozkazu ze statusem „czeka na ownera”;
   - najnowszy raport `briefings/RRRR-MM-DD-drift-check-open-sessions.md`: każde pytanie klasy C.
2. Uporządkuj otwarte domknięcia rosnąco według czasu ownera w minutach.
3. Podaj ownerowi co najwyżej 3 ruchy w górę. Każdy ruch ma 3 dane: czynność, czas w minutach, link.
4. Jeżeli owner zleca narzędzie, a liczba otwartych domknięć wynosi co najmniej 3, to dodaj 1 zdanie z tą liczbą. Potem wykonaj zlecenie.
5. Jeżeli najnowszy zapis punktu ma co najmniej 7 dni, to podaj nowy punkt: rozum i śmiałość w procentach, 3 dowody dla każdej osi, kierunek zmiany. Zapisz punkt na stronie SB `projects/boldness-brains-skill.md`, w sekcji „Punkty”.

## Zasady

- Każdy ruch ma 1 zdanie. Agent liczy działania; agent nie ocenia osoby.
- Każda liczba ma źródło: plik albo komendę.
- Ocena w procentach i czas w minutach to oceny agenta, a nie pomiary. Raport podaje ten fakt wprost.
- Skill nie blokuje zlecenia ownera: agent wykonuje zlecenie po sugestii.

## Hook

Hook `hooks/boldness-nudge.py` z repo `claude-code-skills` działa na starcie sesji (SessionStart) po instalacji w katalogu `~/.claude/hooks`. Hook liczy karty, które czekają na ownera, oraz składniki rozkazów ze statusem „czeka na ownera”. Hook wypisuje 1 linię kontekstu z 2 liczbami. Bez danych hook nie wypisuje nic.
