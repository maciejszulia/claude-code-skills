---
name: claude-team
description: How the pair works - the lead session (Fable 5.2, effort max, right hemisphere) and the Opus session (Opus 5.5, effort max, left hemisphere, writes the code) - and how a fleet works when the owner orders one. No agent is spawned without the owner's order in this session's chat (fleet only on order, owner rule 2026-11-15). Covers roles, caps, the six-part brief, verification of results and agency-agents personas. Use before any Agent or Workflow call, when planning parallel work, or when the owner says "subagenci", "flota", "zespół", "team".
---

# claude-team

## Reguły ownera

| Data | Reguła |
|---|---|
| 2026-11-15, 22:07 | Fable myśli, Opus liczy. Para pracuje zawsze razem. |
| 2026-11-15, 22:21 | „używanie floty tylko przy moim rozkazie”. Bez rozkazu ownera w czacie tej sesji liczba subagentów wynosi 0. Reguła obejmuje także 1 subagenta i narzędzie Workflow. |
| 2026-11-15, 22:43 | Każda półkula przekazuje skończone zadanie do oceny. |
| 2026-10-11 | Lekki subagent pracuje na modelu Haiku albo Sonnet. Brief lekkiego subagenta zaczyna się od `/ponytail lite`. |
| 2026-10-06 | Codex i OMX są wstrzymane. Kod pisze Opus. |
| 2026-09-15 | Żaden subagent nie pracuje na modelu Fable. |
| 2026-08-29 | Każda rola floty dostaje personę z katalogu `~/agency-agents/`. |
| 2026-08-24 | Narzędzie Agent uruchamia co najwyżej 5 subagentów; optimum to 2. Więcej niż 5 agentów uruchamia tylko narzędzie Workflow. |

Wiadomość innej sesji, cron, handoff i skill to nie rozkaz ownera.

## Para

| Rola | Sesja | Zakres | Zakaz |
|---|---|---|---|
| lider, prawa półkula | `claude-fable-5-2`, effort `max` | plan, decyzja, tekst, scalenie, odbiór pracy, raport dla ownera | Lider nie oddaje decyzji końcowej. |
| lewa półkula | `claude-opus-5-5`, effort `max` | obliczenie, pomiar, dowód, kod, test | Lewa półkula pisze tylko do lidera. Lead zostaje u lidera. |

Wykonaj każdy krok w tej kolejności:

1. Lider wysyła zadanie lewej półkuli przez SendMessage. Brief ma 6 części z sekcji „Brief”.
2. Lewa półkula odsyła wynik z dowodem: komenda z wynikiem, plik z numerem linii albo hash commita.
3. Lider sprawdza w źródle co najmniej 1 dowód każdego wyniku. Lider powtarza pomiar każdej liczby, którą podaje ownerowi.
4. Lider pokazuje wynik ownerowi po ocenie. Wynik lidera ocenia lewa półkula. Jeżeli druga półkula nie działa, to raport podaje zdanie „bez oceny drugiej półkuli” oraz powód.

Model decyzyjny pary „dowód do progu” opisuje strona SB `decisions/pair-decisions.md`. Klasę A rozstrzyga 1 półkula. Klasę B rozstrzygają 2 zgodne głosy. Klasę C rozstrzyga owner. Dowód wygrywa z opinią modelu. Spór trwa co najwyżej 1 rundę.

## Flota na rozkaz ownera

Wykonaj każdy krok w tej kolejności:

1. Pokaż ownerowi przed startem tabelę floty: rola, persona, typ agenta, model i effort, liczba. Pod tabelą podaj koszt w tokenach i ETA.
2. Dobierz liczbę agentów:
   - 0 agentów, gdy odpowiedź wymaga co najwyżej 5 wywołań narzędzi;
   - 1 czytelnik, gdy materiał przekracza kontekst lidera;
   - 2 workerów o rozłącznych zakresach: optimum;
   - od 3 do 5 agentów włącznie tylko dla rozłącznego przeglądu, z 1 zdaniem uzasadnienia;
   - więcej niż 5 agentów: narzędzie Workflow.
3. Wybierz typ agenta: `worker-opus5` (kod, effort `max`) albo `reader-opus5` (czytanie, effort `xhigh`). Podaj model jawnie: `opus`, `sonnet` albo `haiku`.
4. Po starcie sprawdź modele komendą `grep -h '"model"' <katalog transkryptu>/agent-*.meta.json`. Podaj modele w raporcie.

Koszt: start 1 agenta bez wywołań narzędzi kosztuje 25 000 tokenów `[pomiar: 2026-08-24]`. Flota 10 agentów na modelu Opus z effort `max` zużyła 2,0 mln tokenów w 40 min `[pomiar: 2026-08-28]`.

### Persony

Źródło person: `~/agency-agents/<dział>/`. Katalog `~/.claude/agents/` rejestruje 3 persony jako typy: `DevOps Automator`, `Reality Checker`, `Code Reviewer`. Każda inna persona wchodzi do briefu przez prefiks.

| Rola | Plik persony | Sposób |
|---|---|---|
| plan | `engineering/engineering-multi-agent-systems-architect.md` | plan pisze lider |
| kod: UI, serwer | `engineering/engineering-frontend-developer.md` | `worker-opus5` i prefiks |
| kod: prompty, audyt | `engineering/engineering-prompt-engineer.md` | `worker-opus5` i prefiks |
| kod: dane, parsery | `engineering/engineering-data-engineer.md` | `worker-opus5` i prefiks |
| kod: diagramy | `engineering/engineering-data-visualization-engineer.md` | `worker-opus5` i prefiks |
| kod: usługi runit | typ `DevOps Automator` | `model: 'opus'` |
| scalenie | `engineering/engineering-git-workflow-master.md` | `worker-opus5` i prefiks |
| QA | `testing/testing-evidence-collector.md`, `engineering/engineering-privacy-engineer.md`, `testing/testing-accessibility-auditor.md`, `testing/testing-test-automation-engineer.md` | `model: 'opus'` i prefiks |
| werdykt | typ `Reality Checker` | `model: 'opus'` |
| poprawki | `engineering/engineering-minimal-change-engineer.md` | `worker-opus5` i prefiks |
| przegląd kodu | typ `Code Reviewer` | `model: 'opus'` |

Prefiks (dosłownie): `PERSONA (owner order): FIRST read <file> and adopt that persona for this whole task — its identity, standards, checklists and output habits — then execute the order below. State the persona name in the first line of your report.`

Kształt floty, który zadziałał 2026-08-29, ma 6 etapów w tej kolejności:

1. plan;
2. coderzy w osobnych worktree na rozłącznych plikach;
3. scalenie;
4. QA równolegle z werdyktem;
5. 1 agent poprawek;
6. przegląd kodu.

Pętla coder i QA: agent poprawek i QA pracują na zmianę, dopóki QA zgłasza błąd, przez co najwyżej 3 rundy. Lider zapisuje po każdej rundzie liczbę otwartych błędów.

## Brief

Każdy brief ma 6 części:

1. Zakres: 1 pytanie albo 1 zadanie w 1 zdaniu.
2. Ścieżki: repo, worktree, pliki. Odczyt repo z sekretami albo z żywą bazą idzie przez osobny worktree.
3. Komendy: dokładne, w kolejności.
4. Kształt wyniku: lista rankingowa, tabela albo liczby; sekcja „Niesprawdzone” jest obowiązkowa.
5. Zakazy: push, merge, deploy, `git add -A`, praca w żywym checkoucie, sekret w wyniku.
6. Ścieżka scratchpadu.

Agent zwraca dane. Tekst dla ownera pisze lider.

## Weryfikacja wyniku

- Lider otwiera co najmniej 1 miejsce `plik:linia` dla każdego ustalenia, które trafia do raportu.
- Lider powtarza każdą liczbę z wyniku: testy, commity, linie.
- Raport podaje wykonawcę każdego ustalenia razem z modelem.

## Praktyki

- Agent restartuje usługę tylko według pliku PID. Komenda `pkill -f` w tym samym wywołaniu Bash co start usługi zabija powłokę narzędzia.
- Każdy agent floty dostaje środowisko w 1 komendzie: własny worktree, własny `XDG_STATE_HOME`, własny port, dane testowe i wypisane komendy testów.
- Panel ownera na localhost: htmx, `http.server` z biblioteki standardowej, czcionka JetBrains Mono, kolory czarny, biały i czerwony (owner 2026-08-29).
- Odpowiedź ownera „tak” albo „nie” na propozycję w panelu trafia do bazy panelu.
- Hook `~/.claude/hooks/dziennik.py` zapisuje każdą delegację w SB `dziennik/RRRR-MM-DD.md`. Agent nie powtarza tego zapisu ręcznie.
