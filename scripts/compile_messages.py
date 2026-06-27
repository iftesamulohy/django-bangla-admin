#!/usr/bin/env python
"""Compile all ``django.po`` catalogs to ``django.mo`` (pure Python).

A dependency-free stand-in for ``django-admin compilemessages`` / ``msgfmt`` so
the package can be built without the GNU gettext toolchain installed.

Usage::

    python scripts/compile_messages.py
"""

import array
import os
import re
import struct
import sys


def parse_po(path):
    """Return a {msgid: msgstr} dict from a .po file (basic, no plurals)."""
    entries = {}
    msgid = msgstr = None
    state = None

    def unescape(s):
        return (
            s.replace(r"\n", "\n").replace(r"\t", "\t")
            .replace(r"\"", '"').replace(r"\\", "\\")
        )

    with open(path, encoding="utf-8") as fh:
        for raw in fh:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            m = re.match(r'msgid\s+"(.*)"$', line)
            if m:
                if msgid is not None:
                    entries[msgid] = msgstr or ""
                msgid, msgstr, state = unescape(m.group(1)), "", "id"
                continue
            m = re.match(r'msgstr\s+"(.*)"$', line)
            if m:
                msgstr, state = unescape(m.group(1)), "str"
                continue
            m = re.match(r'"(.*)"$', line)
            if m:
                if state == "id":
                    msgid += unescape(m.group(1))
                elif state == "str":
                    msgstr += unescape(m.group(1))
        if msgid is not None:
            entries[msgid] = msgstr or ""
    return entries


def write_mo(entries, path):
    """Write a GNU .mo file. Empty msgstrs are dropped (fall back to msgid)."""
    # Keep the header (msgid "") plus any non-empty translations.
    items = [(k, v) for k, v in entries.items() if v != "" or k == ""]
    items.sort(key=lambda kv: kv[0].encode("utf-8"))
    keys = b"\x00".join(k.encode("utf-8") for k, _ in items)
    vals = b"\x00".join(v.encode("utf-8") for _, v in items)

    koffsets = []
    voffsets = []
    kcur = vcur = 0
    for k, v in items:
        kb = k.encode("utf-8")
        vb = v.encode("utf-8")
        koffsets.append((len(kb), kcur))
        kcur += len(kb) + 1
        voffsets.append((len(vb), vcur))
        vcur += len(vb) + 1

    n = len(items)
    keystart = 7 * 4 + 16 * n
    valuestart = keystart + len(keys) + (1 if keys else 0)

    offsets = []
    for (klen, koff), (vlen, voff) in zip(koffsets, voffsets):
        offsets.append((klen, keystart + koff, vlen, valuestart + voff))

    output = struct.pack(
        "Iiiiiii",
        0x950412DE,  # magic
        0,           # version
        n,           # number of strings
        7 * 4,       # offset of key table
        7 * 4 + n * 8,  # offset of value table
        0, 0,        # hash table size/offset (unused)
    )
    ids = array.array("i")
    strs = array.array("i")
    for klen, koff, vlen, voff in offsets:
        ids.extend([klen, koff])
        strs.extend([vlen, voff])
    output += ids.tobytes() + strs.tobytes()
    output += keys + (b"\x00" if keys else b"")
    output += vals + (b"\x00" if vals else b"")

    with open(path, "wb") as fh:
        fh.write(output)


def main():
    root = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "django_bangla_admin",
        "locale",
    )
    count = 0
    for dirpath, _dirs, files in os.walk(root):
        for name in files:
            if name.endswith(".po"):
                po = os.path.join(dirpath, name)
                mo = po[:-3] + ".mo"
                entries = parse_po(po)
                write_mo(entries, mo)
                print(f"compiled {os.path.relpath(po, root)} -> {os.path.basename(mo)} ({len(entries)} entries)")
                count += 1
    if count == 0:
        print("No .po files found.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
