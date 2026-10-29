"""Command-line interface for unit-style-checker."""
import argparse
import json

from .core import RULES, check_text


def main(argv=None):
    ap = argparse.ArgumentParser(prog="unit-style-checker", description="Check number/unit formatting.")
    ap.add_argument("file")
    ap.add_argument("--only", help="comma-separated rule codes: " + ", ".join(c for c, _, _ in RULES))
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    with open(args.file, encoding="utf-8", errors="replace") as fh:
        issues, consistency = check_text(fh.read(), set(args.only.split(",")) if args.only else None)
    if args.json:
        print(json.dumps({"issues": [i._asdict() for i in issues], "consistency": consistency}, indent=2, ensure_ascii=False))
    else:
        for i in issues:
            print("%s:%d:%d: [%s] '%s' -> %s" % (args.file, i.line, i.col, i.code, i.match, i.suggestion))
        for c in consistency:
            print("CONSISTENCY: " + c)
        print("%d issue(s)" % len(issues))
    return 1 if issues or consistency else 0
