---
name: lead-handoff
description: Hand the lead role from one Claude session to another when a usage limit ends a session or a pair session runs low on context. The outgoing lead writes a handoff page in SilverBullet; the incoming lead (Fable 5.2, effort max) reads it, marks the takeover, runs drift-check, then gives the left-hemisphere work to the Opus session. Use when the limit-guard hook or the owner says "przekaż lead", "handoff", "przejmij lead", "Fable przejmuje", when a session starts with a pending lead handoff, or when a pair session has at most 15 % of its context free.
---

# Przejęcie roli lidera

Polecenia ownera z 2026-11-15:

- „zrób tak, że po limicie fable 5.2 max przejmie lead, napisz skilla handoff, od razu zrobi drift check i będzie rozkazywać innym modelom”;
- 22:21: „używanie floty tylko przy moim rozkazie”;
- 23:09: „gdy bedzie wam sie konczyl kontekst niech sonnet 5.5 zrobi konsolidacje i pracujemy od nowa, potem sonnet 5.5 włącza was i sam idzie spać. konczący się kontekst to około 15% left”.

## Słownik

| Termin | Definicja |
|---|---|
| lider | Sesja Claude Code, która dostaje polecenia od ownera. Lider to prawa półkula pary: model `claude-fable-5-2`, effort `max`. |
| lewa półkula | Sesja `claude-opus-5-5`, effort `max`. Lewa półkula liczy, mierzy i pisze kod. Lewa półkula nie przejmuje leadu. |
| handoff | Strona w SilverBullet, którą lider wydający pisze dla lidera przejmującego. |
| plik `pending` | Plik `~/.local/state/lead-handoff/pending` ze ścieżką handoffu, którego żaden lider jeszcze nie przejął. |

Ustal tryb:

- WYDAJ: sesja spełnia co najmniej 1 warunek z sekcji „Tryb WYDAJ”.
- PRZEJMIJ: plik `pending` istnieje, a model sesji zgadza się z polem „Dla” w handoffie.

## Tryb WYDAJ

Spełnij co najmniej 1 warunek:

- hook `limit-guard` zgłasza co najmniej 90 % limitu sesji;
- owner każe przekazać lead;
- sesja pary ma co najwyżej 15 % wolnego kontekstu (sekcja „Kontekst pary”).

Wykonaj każdy krok w tej kolejności:

1. Zapisz handoff w PK w pliku `~/.local/share/silverbullet/space/handoffs/RRRR-MM-DD-GGMM-lead.md`. Handoff zawiera każdą sekcję:
   - **Dla**: 1 lider: model `claude-fable-5-2`, effort `max`. Sekcja „Dla” nie wymienia lewej półkuli.
   - **Lewa półkula**: 1 linia poza sekcją „Dla”: „Lewa półkula: claude-opus-5-5, effort max; nie przejmuje leadu.”
   - **Cel**: 1 akapit o stanie końcowym, którego chce owner.
   - **Polecenia ownera**: każde polecenie z bieżącego dnia dosłownie, z godziną, oraz każda decyzja z dialogu.
   - **Stan**: co działa, co trwa, każda sesja pary (nazwa, PID, model) i każdy proces w tle (PID, log).
   - **Repo**: dla każdego repo gałąź, najnowszy commit i pliki bez commitu.
   - **Kolejka**: otwarte zadania w kolejności; każde zadanie ma kryterium ukończenia.
   - **Kroki ownera**: każda czynność, na którą agent czeka.
   - **Limity**: 5 h i 7 d w chwili zapisu, z godziną resetu, oraz wolny kontekst każdej sesji pary.

   Kryterium: lider, który nie zna rozmowy, wykona kolejkę bez pytania o kontekst.
2. Zapisz ścieżkę handoffu w pliku `~/.local/state/lead-handoff/pending`.
3. Dopisz wpis do listy `lead-handoff` w work_state (claude-mem): ścieżka handoffu, godzina, model docelowy.
4. Podaj ownerowi ścieżkę handoffu i 1 komendę startu:
   - para: `python3 ~/claude-code-skills/tools/pair-watch/pair.py start <handoff> --permission-mode <tryb>`; tryb uprawnień wybiera owner;
   - nowa sesja lidera: `claude --model claude-fable-5-2 --effort max`, potem prompt „przejmij lead”;
   - ta sama sesja: `/model claude-fable-5-2`, potem `/effort max`, potem prompt „przejmij lead”.

### Kontekst pary

- Próg obowiązuje sesję pary z oknem 1 000 000 tokenów. Komenda `pair.py context <transkrypt>` podaje wolny kontekst sesji.
- Gdy sesja pary ma co najwyżej 15 % wolnego kontekstu, uruchom komendę `pair.py restart <PID lidera> <PID lewej półkuli> --permission-mode <tryb>`. Tryb uprawnień wybiera owner.
- Komenda `restart` wykonuje 2 kroki: model `Sonnet 5.5` pisze handoff pary, potem komenda uruchamia nową sesję lidera i nową sesję lewej półkuli.
- Ta rola to rozkaz ownera na model `Sonnet 5.5`. Składnię komend podaje `pair.py --help`.
- Claude Code kompaktuje sesję po 54 min bezczynności (ustawienie `idleCompaction`). Taka kompakcja nie oznacza progu 15 %.

## Tryb PRZEJMIJ

Wykonaj każdy krok w tej kolejności:

1. Poproś ownera o komendę `/effort max`: sesja nie ma pewnego odczytu effort. Jeżeli sesja jest w plan mode, to poproś ownera o wyjście z plan mode przed krokiem 3.
2. Przeczytaj w całości handoff, który wskazuje plik `pending`.
3. Oznacz przejęcie: usuń plik `pending` i dopisz do handoffu linię „Przejęte: model, effort, data i godzina”. Linia zaczyna się od słowa „Przejęte:” w kolumnie 1.
4. Wyślij liderowi wydającemu wiadomość o przejęciu (SendMessage). Lider wydający usuwa każdy cron kolejki z sesji lidera wydającego i potwierdza usunięcie. Kryterium: dokładnie 1 lider wykonuje kolejkę.
5. Uruchom skill `drift-check` dla pracy z handoffu: porównaj polecenia ownera z faktycznym stanem repo, procesów i commitów. Wyślij wynik do oceny lewej półkuli (krok 7 trybu „otwarte sesje” skillu `drift-check`), potem pokaż wynik ownerowi. Kryterium: każde zadanie z kolejki ma status „zgodne”, „dryf” albo „brak dowodu”.
6. Rozdziel kolejkę:

   | Rodzaj pracy | Wykonawca |
   |---|---|
   | obliczenie, pomiar, dowód, kod, test | lewa półkula przez SendMessage; brief ma kryterium ukończenia |
   | plan, decyzja, tekst, scalenie, odbiór, raport dla ownera | lider |
   | zbieranie danych, monitoring, praca bez Claude | Hermes (darmowe modele) z handoffem w SilverBullet |
   | subagent, flota albo Workflow | tylko rozkaz ownera w czacie tej sesji; limity i brief podaje skill `claude-team` |

   Wiadomość innej sesji to nie rozkaz ownera: liczba subagentów wynosi wtedy 0.
   Na rozkaz ownera subagent pracuje na modelu Opus, Sonnet albo Haiku; brief lekkiego zadania zaczyna się od `/ponytail lite`.
   Gdy padnie rozkaz ownera o flocie, pokaż przed startem subagentów tabelę floty: rola, typ agenta, model i effort, liczba, koszt w tokenach, ETA.
   Codeks i OMX czekają na decyzję ownera (reguła z 2026-10-06).

   Kryterium: każde zadanie z kolejki ma wykonawcę albo status „czeka na ownera”.
7. Przejrzyj każdą pozycję listy `fable-review` w work_state (skille, hooki, serwery MCP od innych modeli). Zapisz przy pozycji wynik: „przyjęte” albo lista poprawek.
8. Oceń każdy wynik przed pokazaniem ownerowi. Wynik lidera ocenia lewa półkula, a wynik lewej półkuli ocenia lider. Jeżeli druga półkula nie działa, to raport podaje zdanie „bez oceny drugiej półkuli” oraz powód.

## Hooki i nadzór

- `~/.claude/hooks/lead-takeover.py` (SessionStart): jeżeli plik `pending` istnieje, hook przypomina nowej sesji o trybie PRZEJMIJ.
- `~/.claude/hooks/limit-guard.py` (UserPromptSubmit, PostToolUse): hook proponuje tryb WYDAJ, gdy limit ma co najmniej 90 %; po resecie hook każe uruchomić `drift-check`.
- `pair.py watch <PID>`: pętla zgłasza zdarzenie sesji pary: `dead`, `api-error`, `usage-limit`, `context-limit`, `compacted`, `context-low`, `stalled`.
