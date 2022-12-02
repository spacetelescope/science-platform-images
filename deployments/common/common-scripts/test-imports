#! /usr/bin/env python
# -*-python-*-

"""Import the packages listed on the command line to test installation."""

import sys
import traceback


def flush():
    sys.stdout.flush()
    sys.stderr.flush()


def fprint(*args, **keys):
    print(*args, **keys)
    flush()


if len(sys.argv) < 2:
    print("test-imports <pkgs...>", file=sys.stderr)
    sys.exit(1)

import_list = sys.argv[1:]

errs = []
for pkg in import_list:
    if pkg.startswith("#"):
        fprint("Skipping", pkg)
        continue
    try:
        fprint("Importing", pkg, "... ", end="")
        __import__(pkg)
        fprint("ok")
    except Exception:
        traceback.print_exc()
        fprint("FAIL")
        errs.append(pkg)
    flush()
fprint("=" * 80)
fprint(
    f" Failing imports: {len(errs)} ".center(80, "=") + "\n", "\n".join(errs), sep=""
)
sys.exit(int(len(errs) != 0))
