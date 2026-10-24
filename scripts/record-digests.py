#!/usr/bin/env python3
"""Records digests in catalog.json (ADR 0095).

The build workflow calls this after it pushes. It reads lines of
"<kind> <key> <field> <digest>" on stdin, for example

    php 8.4 digest sha256:...
    php 8.4 upstreamDigest sha256:...
    node 22 digest sha256:...
    bun - digest sha256:...

and rewrites the catalog with those digests. With --repository <name> it
also sets phpRepository, the registry path the images were pushed to. It refuses anything else, so a
malformed line never lands in the catalog. A person reviews and commits the
result; nothing here commits or pushes.
"""
import json
import re
import sys
from pathlib import Path

DIGEST = re.compile(r"^sha256:[0-9a-f]{64}$")
REPOSITORY = re.compile(r"^[a-z0-9][a-z0-9._:-]*(/[a-z0-9][a-z0-9._-]*)+$")
args = sys.argv[1:]
repository = None
if len(args) >= 2 and args[0] == "--repository":
    repository = args[1]
    args = args[2:]
    if not REPOSITORY.match(repository) or len(repository) > 255:
        sys.exit("--repository must be a lowercase registry path such as ghcr.io/kongpda/deplr-php")
catalog_path = Path(args[0] if args else Path(__file__).resolve().parent.parent / "catalog.json")
catalog = json.loads(catalog_path.read_text())
if repository is not None:
    catalog["phpRepository"] = repository

for number, raw in enumerate(sys.stdin, start=1):
    line = raw.strip()
    if not line:
        continue
    parts = line.split()
    if len(parts) != 4 or not DIGEST.match(parts[3]):
        sys.exit(f"line {number}: expected '<kind> <key> <field> sha256:<64 hex>'")
    kind, key, field, digest = parts
    if kind == "php" and field in ("digest", "upstreamDigest"):
        entries = [entry for entry in catalog["php"] if entry["minor"] == key]
    elif kind == "node" and field == "digest":
        entries = [entry for entry in catalog["node"] if str(entry["major"]) == key]
    elif kind == "bun" and field == "digest" and key == "-":
        entries = [catalog["bun"]]
    else:
        sys.exit(f"line {number}: unknown entry {kind} {key} {field}")
    if not entries:
        sys.exit(f"line {number}: {kind} {key} is not in the catalog")
    for entry in entries:
        entry[field] = digest

catalog_path.write_text(json.dumps(catalog, indent=2) + "\n")
