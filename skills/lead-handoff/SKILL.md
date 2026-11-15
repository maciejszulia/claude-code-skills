---
name: lead-handoff
description: Hand the lead role from one Claude model to another when a usage limit ends a session. The outgoing lead writes a handoff page in SilverBullet; the incoming lead (default Fable 5.2, effort max) reads it, runs drift-check first, then assigns the open work to other models. Use when the limit-guard hook or the owner says "przekaż lead", "handoff", "przejmij lead", "Fable przejmuje", or when a session starts with a pending lead handoff.
---

# Przejęcie roli lidera

Owner 2026-11-15: „zrób tak, że po limicie fable 5.2 max przejmie lead, napisz skilla handoff, od razu zrobi drift check i będzie rozkazywać innym modelom”.

Lider oznacza sesję Claude Code, która dostaje polecenia od ownera. Handoff oznacza stronę w SilverBullet, którą lider wydający pisze dla lidera przejmującego. Plik `~/.local/state/lead-handoff/pending` zawiera ścieżkę handoffu, którego żaden lider jeszcze nie przejął.

Ustal tryb:

- WYDAJ: limit twojej sesji dochodzi do końca albo owner każe przekazać lead.
- PRZEJMIJ: plik `pending` istnieje i twój model zgadza się z polem „Dla” w handoffie.

## Tryb WYDAJ

Wykonaj każdy krok w tej kolejności:

1. Zapisz handoff w PK w pliku `~/.local/share/silverbullet/space/handoffs/RRRR-MM-DD-GGMM-lead.md`. Handoff zawiera każdą sekcję:
   - **Dla**: model i effort lidera przejmującego; domyślnie `claude-fable-5-2`, effort `max`.
   - **Cel**: 1 akapit o stanie końcowym, którego chce owner.
   - **Polecenia ownera**: każde polecenie z bieżącego dnia dosłownie, z godziną, oraz każda decyzja z dialogu.
   - **Stan**: co działa, co trwa, każdy subagent w toku (opis, model, ścieżka) i każdy proces w tle (PID, log).
   - **Repo**: dla każdego repo gałąź, najnowszy commit i pliki bez commitu.
   - **Kolejka**: otwarte zadania w kolejności; każde zadanie ma kryterium ukończenia.
   - **Kroki ownera**: każda czynność, na którą agent czeka.
   - **Limity**: 5 h i 7 d w chwili zapisu, z godziną resetu.

   Kryterium: lider, który nie zna rozmowy, wykona kolejkę bez pytania o kontekst.
2. Zapisz ścieżkę handoffu w pliku `~/.local/state/lead-handoff/pending`.
3. Dopisz wpis do listy `lead-handoff` w work_state (claude-mem): ścieżka handoffu, godzina, model docelowy.
4. Podaj ownerowi ścieżkę handoffu i 1 komendę startu lidera przejmującego:
   - nowa sesja: `claude --model claude-fable-5-2 --effort max`, potem prompt „przejmij lead”;
   - ta sama sesja: `/model claude-fable-5-2`, potem `/effort max`, potem prompt „przejmij lead”.

## Tryb PRZEJMIJ

Wykonaj każdy krok w tej kolejności:

1. Przeczytaj w całości handoff, który wskazuje plik `pending`.
2. Uruchom skill `drift-check` dla pracy z handoffu: porównaj polecenia ownera z faktycznym stanem repo, procesów i commitów. Pokaż wynik ownerowi. Kryterium: każde zadanie z kolejki ma status „zgodne”, „dryf” albo „brak dowodu”.
3. Usuń plik `pending`. Dopisz do handoffu linię „Przejęte: model, effort, data i godzina”.
4. Rozdziel kolejkę według skillu `claude-team` (role, limity, brief z 6 części, weryfikacja wyniku):

   | Rodzaj pracy | Wykonawca |
   |---|---|
   | kod, ewaluacja, praca dłuższa niż 1 h | subagent `worker-opus5`, `model: "opus"`, effort `max` albo `xhigh` |
   | czytanie całego repo, weryfikacja | subagent `reader-opus5` |
   | lekkie zadanie na prośbę ownera | subagent Sonnet albo Haiku; brief zaczyna się od `/ponytail lite` |
   | zbieranie danych, monitoring, praca bez Claude | Hermes (darmowe modele) z handoffem w SilverBullet |

   Lider zostaje przy decyzjach, odbiorze pracy i raporcie dla ownera. Każdy subagent pracuje na modelu Opus, Sonnet albo Haiku (reguła ownera z 2026-09-15). Codeks i OMX czekają na decyzję ownera (reguła z 2026-10-06).

   Kryterium: każde zadanie z kolejki ma wykonawcę albo status „czeka na ownera”.
5. Przed startem subagentów pokaż ownerowi tabelę floty (rola, typ agenta, model i effort, liczba), koszt w tokenach i ETA.

## Hooki

- `~/.claude/hooks/lead-takeover.py` (SessionStart): jeżeli plik `pending` istnieje, hook przypomina nowej sesji o trybie PRZEJMIJ.
- `~/.claude/hooks/limit-guard.py` (UserPromptSubmit, PostToolUse): przy limicie od 90 % proponuje tryb WYDAJ; po resecie każe uruchomić `drift-check`.
