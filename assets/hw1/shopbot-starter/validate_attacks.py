"""Validate ShopBot attack submissions without importing or running student code."""
import json
import sys
from pathlib import Path

FIELDS = {'id', 'strategy', 'logged_in_customer', 'messages'}
MESSAGE_FIELDS = {'role', 'content'}


def validate(path):
    try:
        attacks = json.loads(Path(path).read_text(encoding='utf-8'))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f'Cannot read valid JSON: {exc}') from exc
    if not isinstance(attacks, list) or len(attacks) < 3:
        raise ValueError('Expected a JSON array containing at least three attacks.')
    seen = set()
    for index, entry in enumerate(attacks, 1):
        if not isinstance(entry, dict) or set(entry) != FIELDS:
            raise ValueError(f'Attack #{index}: fields must be exactly {sorted(FIELDS)}')
        aid = entry['id']
        if not isinstance(aid, str) or not aid.strip() or aid in seen:
            raise ValueError(f'Attack #{index}: id must be a unique nonempty string')
        seen.add(aid)
        if not isinstance(entry['strategy'], str) or not entry['strategy'].strip():
            raise ValueError(f'{aid}: strategy must be a nonempty string')
        if type(entry['logged_in_customer']) is not int or entry['logged_in_customer'] <= 0:
            raise ValueError(f'{aid}: logged_in_customer must be a positive integer')
        messages = entry['messages']
        if not isinstance(messages, list) or not messages:
            raise ValueError(f'{aid}: messages must be a nonempty array')
        for j, message in enumerate(messages, 1):
            if not isinstance(message, dict) or set(message) != MESSAGE_FIELDS:
                raise ValueError(f'{aid}: message #{j} must have exactly role and content')
            if message['role'] != 'user' or not isinstance(message['content'], str) or not message['content'].strip():
                raise ValueError(f'{aid}: message #{j} must have role=user and nonempty text')
            if 'REPLACE THIS WITH YOUR ATTACK' in message['content']:
                raise ValueError(f'{aid}: replace the template placeholder')
    print(f'PASS: {len(attacks)} attacks, unique IDs, exact schema, no placeholders')


if __name__ == '__main__':
    try:
        validate(sys.argv[1] if len(sys.argv) > 1 else 'attacks.json')
    except ValueError as exc:
        print(f'FAIL: {exc}', file=sys.stderr)
        sys.exit(1)
