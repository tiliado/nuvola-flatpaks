#!/usr/bin/env python3
import os
import re
import sys
from typing import Dict, List, Pattern, Set, Tuple


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
    assert not group, group
    return re.compile("".join(regex))


def collect_entries(directory: str) -> List[str]:
    return sorted(
        os.path.join(root if not root.startswith("./") else root[2:], name) if root != "." else name
        for root, _dirs, files in os.walk(directory, followlinks=False)
        for name in files
    )


def read_rules(paths: Set[str], patterns: Dict[Tuple[str, Pattern[str]], int], file: str) -> None:
    with open(file) as f:
        for line in f:
            path = line.strip()
            if path and not path.startswith("#"):
                if "*" in path or "?" in path or "{" in path:
                    patterns[(path, compile_pattern(path.lstrip("@")))] = 0
                else:
                    assert path not in paths
                    paths.add(path)


def process_entries(paths: Set[str], patterns: Dict[Tuple[str, Pattern[str]], int], entries: List[str]) -> List[str]:
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

    return extra


def print_summary(paths: Set[str], patterns: Dict[Tuple[str, Pattern[str]], int], extra: List[str]) -> bool:
    success = not extra and not paths

    if extra:
        print("Extra entries:", file=sys.stderr)
        for entry in extra:
            print("!", entry, file=sys.stderr)

    if paths:
        print("Unused paths:", file=sys.stderr)
        for entry in paths:
            print("!", entry, file=sys.stderr)
    if patterns:
        print("Patterns:", file=sys.stderr)
        for (pattern, _matcher), count in patterns.items():
            if not count and not pattern.startswith("@"):
                success = False
                print("!", pattern, count, file=sys.stderr)
            else:
                print(" ", pattern, count, file=sys.stderr)

    return success


def main(argv: List[str]) -> int:
    directory = argv[1] if len(argv) > 1 else "."
    entries = collect_entries(directory)
    print("\n".join(entries), file=sys.stdout)

    patterns = {}
    paths = set()

    for file in argv[2:]:
        read_rules(paths, patterns, file)

    extra = process_entries(paths, patterns, entries)
    success = print_summary(paths, patterns, extra)
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
