#!/usr/bin/env python3
import os
import sys
import fnmatch 
from typing import List, Set

result = 0
directory = sys.argv[1] if len(sys.argv) > 1 else '.'

entries: List[str] = sorted(
    os.path.join(root if not root.startswith('./') else root[2:], name) if root != '.' else name
    for root, _dirs, files in os.walk(directory, followlinks=False)
    for name in files
)
# ~ print('\n'.join(entries), file=sys.stdout)

if len(sys.argv) > 2:
    allowed_patterns: List[str] = []
    append = allowed_patterns.append
    remaining_entries: Set[str] = set(entries)
    discard = remaining_entries.discard
    for path in sys.argv[2:]:
        with open(path) as f:
            for line in f:
                path = line.strip()
                if path:
                    if '*' in path or '?' in path:
                        append(path)
                    elif path in remaining_entries:
                        print(path)
                        discard(path)
    while remaining_entries and allowed_patterns:
        matched_entries = fnmatch.filter(remaining_entries, allowed_patterns.pop())
        remaining_entries.difference_update(matched_entries)
        for entry in matched_entries:
            print(entry)
    if remaining_entries:
        result = 1
        for entry in sorted(remaining_entries):
            print('!', entry, file=sys.stderr)
sys.exit(result)
