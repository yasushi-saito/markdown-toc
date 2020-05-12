#!/usr/bin/env python3.8
import argparse
import re

from typing import List


def to_bullet(depth: int) -> str:
    if depth == 0:
        return "- "
    return " " * depth * 2 + "* "


def to_ref(s: str) -> str:
    s = s.replace(".", "")
    s = s.replace(" ", "-")
    s = s.lower()
    return s


def process_file(path: str, min_depth: int, max_toc_depth: int) -> str:
    with open(path) as fd:
        lines = fd.readlines()
    section_numbers: List[int] = []
    new_lines: List[str] = []
    toc_lines: List[str] = []
    in_code_block = False
    for line in lines:
        if re.match(r"^\s*```", line):
            in_code_block = not in_code_block
        m = re.match(r"^(#+) ([\d.]+)? (.*)", line)
        if m and not in_code_block:
            depth = len(m[1]) - min_depth
            if depth < 0:
                new_lines.append(line)
                continue
            while len(section_numbers) <= depth:
                section_numbers.append(0)
            section_numbers[depth] += 1
            section_numbers = section_numbers[: depth + 1]
            nn = ".".join([f"{n}" for n in section_numbers])
            if len(section_numbers)==1:
                nn += "."
            subject = f"{nn} {m[3]}"
            line = f"{m[1]} {subject}\n"
            if depth <= max_toc_depth:
                toc_lines.append(
                    f"{to_bullet(depth)}[{subject}](#{to_ref(subject)})\n"
                )
        new_lines.append(line)

    lines, new_lines = new_lines, []
    in_toc = False
    for line in lines:
        if line.startswith("<!-- toc -->"):
            in_toc = True
            new_lines.append(line)
            new_lines.append("\n")
            new_lines += toc_lines
            new_lines.append("\n")
            continue
        if line.startswith("<!-- tocstop -->"):
            in_toc = False
        if not in_toc:
            new_lines.append(line)
    return "".join(new_lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--min-depth", type=int, default=2)
    parser.add_argument("--max-toc-depth", type=int, default=3)
    parser.add_argument(
        "--inplace", "-i", action="store_true", help="Update files in place"
    )
    parser.add_argument("file", nargs="*")
    args = parser.parse_args()
    for path in args.file:
        out = process_file(path, args.min_depth, args.max_toc_depth)
        if args.inplace:
            with open(path, 'w') as fd:
                fd.write(out)
        else:
            print(out, end='')

if __name__ == "__main__":
    main()
