"""Copy generated/numbers.tex, adding a thousands separator ({,}) to integer
values of 1000 or more (journal style). Values are not changed.
    python -I fmt_numbers.py <in> <out>"""
import re
import sys


def group(n):
    head = len(n) % 3 or 3
    return "{,}".join([n[:head]] + re.findall("...", n[head:]))


s = open(sys.argv[1], encoding="utf-8").read()
s = re.sub(r"(\\newcommand\{\\\w+\}\{)(\d{4,})(\})", lambda m: m.group(1) + group(m.group(2)) + m.group(3), s)
open(sys.argv[2], "w", encoding="utf-8").write(s)
