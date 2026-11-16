#!/usr/bin/env python3
"""SessionStart hook: counts the closings that wait for the owner and nudges one move up before new tooling.

Owner order of 2026-11-16 (skill boldness-brains): suggest how to move on the boldness-to-brains plane.
Sources, read only:
  - job-application ledgers `portal-submissions.jsonl` in the cv-it repo: a card waits for the owner when it
    has a `filled-awaiting-owner` row and no later `submitted` row (note rows such as `cv-updated` keep it open);
  - `orders/orders.json` in the second-brain space: order components with status "czeka na ownera".
Prints one context line, or nothing when both counts are 0 or a source cannot be read. Never blocks a session.
Usage: boldness-nudge.py < event.json
       boldness-nudge.py --selftest
"""
import json
import sys
import tempfile
from pathlib import Path

LEDGERS = Path.home() / 'Documents' / 'cv-it' / 'claude-2026-09-20' / 'research'
ORDERS = Path.home() / '.local' / 'share' / 'silverbullet' / 'space' / 'orders' / 'orders.json'
WAITING = 'czeka na ownera'


def open_cards(ledgers):
    """Keys whose latest decisive row is filled-awaiting-owner."""
    state = {}
    for path in ledgers:
        for line in path.read_text(encoding='utf-8').splitlines():
            if line.strip():
                row = json.loads(line)
                if row.get('state') in ('filled-awaiting-owner', 'submitted'):
                    state[row.get('key')] = row['state']
    return sum(s == 'filled-awaiting-owner' for s in state.values())


def waiting_components(orders_path):
    if not orders_path.exists():
        return 0
    orders = json.loads(orders_path.read_text(encoding='utf-8')).get('orders') or []
    return sum(c.get('status') == WAITING for o in orders for c in o.get('components') or [])


def line(ledger_dir, orders_path):
    cards = open_cards(sorted(ledger_dir.glob('*/portal-submissions.jsonl'))) if ledger_dir.exists() else 0
    parts = waiting_components(orders_path)
    if not (cards or parts):
        return None
    return (f'boldness-nudge: {cards} kart zgłoszeń czeka na ownera; {parts} składników rozkazów ma status '
            f'„{WAITING}”. Zaproponuj ownerowi 1 ruch w górę przed nowym narzędziem (skill boldness-brains).')


def selftest():
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        (tmp / 'batch').mkdir()
        rows = [('a', 'filled-awaiting-owner'), ('b', 'filled-awaiting-owner'), ('b', 'cv-updated'),
                ('c', 'filled-awaiting-owner'), ('c', 'submitted'), ('d', 'submitted')]
        (tmp / 'batch' / 'portal-submissions.jsonl').write_text(
            ''.join(json.dumps({'key': k, 'state': s}) + '\n' for k, s in rows), encoding='utf-8')
        orders = tmp / 'orders.json'
        orders.write_text(json.dumps({'orders': [{'components': [{'status': WAITING}, {'status': 'wykonany'}]}]}),
                          encoding='utf-8')
        text = line(tmp, orders)
        assert text and text.startswith('boldness-nudge: 2 kart') and '; 1 składników' in text, text
        assert line(tmp / 'missing', tmp / 'missing.json') is None
    print('ok')


def main():
    if sys.argv[1:] == ['--selftest']:
        selftest()
        return 0
    try:
        sys.stdin.read()  # the SessionStart event is not needed
        text = line(LEDGERS, ORDERS)
    except (OSError, ValueError, AttributeError, TypeError):
        return 0  # a read error never blocks the session
    if text:
        print(text)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
