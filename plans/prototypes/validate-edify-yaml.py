#!/usr/bin/env python3
import yaml, tomllib

d = yaml.safe_load(open(".edify.yaml"))
v = tomllib.load(open("pyproject.toml", "rb"))["project"]["version"]
assert d["version"] == v, f"version mismatch: {d['version']} != {v}"
assert d["sync_policy"] == "nag", f"sync_policy wrong: {d['sync_policy']}"
print("OK")
