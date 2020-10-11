#!/usr/bin/env python3
import os
import sys
import re
from typing import List, Dict, Set, Pattern

def compile_pattern(pattern: str) -> Pattern[str]:
    regex = ["^"]
    group = 0
    for char in pattern:
        if char == "?":
            regex.append(".")
        if char == "*":
            regex.append(".*")
        elif char == "{":
            group += 1
            regex.append("(?:")
        elif char == "}":
            assert group
            group -= 1
            regex.append(")")
        elif group and char == ",":
            regex.append("|")
        else:
            regex.append(re.escape(char))
    regex.append("$")
    return re.compile(''.join(regex))


result = 0
directory = sys.argv[1] if len(sys.argv) > 1 else '.'

entries: List[str] = sorted(
    os.path.join(root if not root.startswith('./') else root[2:], name) if root != '.' else name
    for root, _dirs, files in os.walk(directory, followlinks=False)
    for name in files
)
print('\n'.join(entries), file=sys.stdout)

if len(sys.argv) > 2:
    patterns: Dict[Pattern[str], int] = {}
    paths: Set[str] = set()


    if len(sys.argv) > 3:
        with open(sys.argv[3]) as f:
            paths = {line.strip() for line in f}

    with open(sys.argv[2]) as f:
        for line in f:
            path = line.strip()
            if path and not path.startswith("#"):
                if '*' in path or '?' in path or '{' in path:
                    patterns[(path, compile_pattern(path.lstrip("@")))] = 0
                else:
                    assert path not in paths
                    paths.add(path)
    extra = []

    for entry in entries:
        try:
            paths.remove(entry)
        except KeyError:
            for pattern in patterns:
                if pattern[1].match(entry):
                    patterns[pattern] += 1
                    break
            else:
                extra.append(entry)

    success = not extra and not paths

    if extra:
        print("Extra entries:", file=sys.stderr)
        for entry in extra:
            print('!', entry, file=sys.stderr)

    if paths:
        print("Unused paths:", file=sys.stderr)
        for entry in paths:
            print('!', entry, file=sys.stderr)
    if patterns:
        print("Patterns:", file=sys.stderr)
        for (pattern, _matcher), count in patterns.items():
            if not count and not pattern.startswith("@"):
                success = False
                print('!', pattern, count, file=sys.stderr)
            else:
                print(' ', pattern, count, file=sys.stderr)

sys.exit(0 if success else 1)
