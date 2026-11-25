#!/usr/bin/env python3
"""Translation workflow helpers for the Joomla ko-KR pack.

  work.py status                      progress per client
  work.py todo  CLIENT FILE [START N] numbered untranslated strings of a file
  work.py apply CLIENT FILE BATCH     merge "N|korean" lines (numbers from `todo`)
  work.py check                       validate every ko-KR file against en-GB

CLIENT is site | admin | api. English source: $JOOMLA_SRC (a Joomla 6.2.x checkout).
Only translated keys are written; Joomla falls back to en-GB for the rest.
"""
import os, re, sys, glob

SRC = os.environ.get("JOOMLA_SRC", "/home/user/joomla/joomla-cms")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EN = {"site": "language", "admin": "administrator/language", "api": "api/language"}
LINE = re.compile(r'^([^=;\s][^=]*?)\s*=\s*"(.*)"\s*(;.*)?$')
HEADER = ("; Joomla! Project\n; (C) 2005 Open Source Matters, Inc. <https://www.joomla.org>\n"
          "; License GNU General Public License version 2 or later; see LICENSE.txt\n"
          "; Note : All ini files need to be saved as UTF-8\n\n")

def read(path):
    out = {}
    if os.path.exists(path):
        for ln in open(path, encoding="utf-8"):
            m = LINE.match(ln.rstrip("\n"))
            if m:
                out[m.group(1)] = m.group(2)
    return out

def en_path(client, f): return os.path.join(SRC, EN[client], "en-GB", f)
def ko_path(client, f): return os.path.join(ROOT, client, f)
def ini_files(client):
    return sorted(os.path.basename(p) for p in glob.glob(en_path(client, "*.ini")))

def tokens(s):
    return sorted(re.findall(r"%(?:\d+\$)?[sdfu]|%%|\{[A-Za-z0-9_]+\}|</?[A-Za-z][^>]*>|\\n|&#?\w+;|\[[A-Za-z0-9_]+\]|\$\{?\w+\}?", s))

def todo(client, f, start=1, n=80):
    en, ko = read(en_path(client, f)), read(ko_path(client, f))
    pend = [(k, v) for k, v in en.items() if k not in ko]
    for i, (k, v) in enumerate(pend[start - 1:start - 1 + n], start):
        print(f"{i}\t{k}\t{v}")
    print(f"# {len(pend)} untranslated in {client}/{f}", file=sys.stderr)

def apply(client, f, batch):
    en, ko = read(en_path(client, f)), read(ko_path(client, f))
    pend = [k for k in en if k not in ko]
    for ln in open(batch, encoding="utf-8"):
        ln = ln.rstrip("\n")
        if not ln.strip() or ln.startswith("#"): continue
        m = re.match(r"^(\d+)[\t|](.*)$", ln)
        if not m: sys.exit(f"bad batch line: {ln[:60]}")
        num, val = m.groups()
        k = pend[int(num) - 1]
        val = val.strip()
        if en[k].endswith(' ') and not val.endswith(' '): val += ' '
        ko[k] = val
    write(client, f, en, ko)

def write(client, f, en, ko):
    os.makedirs(os.path.join(ROOT, client), exist_ok=True)
    with open(ko_path(client, f), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(HEADER)
        for k in en:
            if k in ko:
                fh.write(f'{k}="{ko[k]}"\n')

def status():
    tot = done = 0
    for c in EN:
        t = d = 0
        for f in ini_files(c):
            en, ko = read(en_path(c, f)), read(ko_path(c, f))
            t += len(en); d += len([k for k in ko if k in en])
        print(f"{c:6} {d:6}/{t:<6} {100*d/max(t,1):5.1f}%"); tot += t; done += d
    print(f"total  {done:6}/{tot:<6} {100*done/tot:5.1f}%")

def check():
    bad = 0
    for c in EN:
        for p in sorted(glob.glob(os.path.join(ROOT, c, "*.ini"))):
            f = os.path.basename(p)
            en = read(en_path(c, f))
            for ln_no, ln in enumerate(open(p, encoding="utf-8"), 1):
                s = ln.rstrip("\n")
                if not s.strip() or s.startswith(";"): continue
                m = LINE.match(s)
                if not m: print(f"{c}/{f}:{ln_no}: unparsable"); bad += 1; continue
                k, v = m.group(1), m.group(2)
                if k not in en: print(f"{c}/{f}:{ln_no}: unknown key {k}"); bad += 1; continue
                if re.search(r'(?<!\\)"', v): print(f"{c}/{f}:{ln_no}: unescaped quote in {k}"); bad += 1
                if tokens(v) != tokens(en[k]):
                    print(f"{c}/{f}:{ln_no}: placeholders differ in {k}: {tokens(en[k])} vs {tokens(v)}"); bad += 1
                if not v.strip(): print(f"{c}/{f}:{ln_no}: empty {k}"); bad += 1
    print("OK" if not bad else f"{bad} problem(s)")
    return bad


# --- reuse: copy a translation to another file's key when key AND English are identical
def reuse():
    pool = {}
    for c in EN:
        for f in ini_files(c):
            en, ko = read(en_path(c, f)), read(ko_path(c, f))
            for k, v in ko.items():
                if k in en: pool[(k, en[k])] = v
    n = 0
    for c in EN:
        for f in ini_files(c):
            en, ko = read(en_path(c, f)), read(ko_path(c, f))
            add = {k: pool[(k, v)] for k, v in en.items() if k not in ko and (k, v) in pool}
            if add:
                ko.update(add); write(c, f, en, ko); n += len(add)
    print(f"reused {n} translations")


def reuse_text():
    """Same English text under another key: reuse when every existing translation of it agrees."""
    seen = {}
    for c in EN:
        for f in ini_files(c):
            en, ko = read(en_path(c, f)), read(ko_path(c, f))
            for k, v in ko.items():
                if k in en: seen.setdefault(en[k], set()).add(v)
    n = 0
    for c in EN:
        for f in ini_files(c):
            en, ko = read(en_path(c, f)), read(ko_path(c, f))
            add = {k: next(iter(seen[v])) for k, v in en.items()
                   if k not in ko and v in seen and len(seen[v]) == 1 and len(v) > 2}
            if add:
                ko.update(add); write(c, f, en, ko); n += len(add)
    print(f"reused {n} by identical English text")

if __name__ == "__main__":
    a = sys.argv[1:]
    if not a: sys.exit(__doc__)
    if a[0] == "status": status()
    elif a[0] == "todo": todo(a[1], a[2], int(a[3]) if len(a) > 3 else 1, int(a[4]) if len(a) > 4 else 80)
    elif a[0] == "apply": apply(a[1], a[2], a[3])
    elif a[0] == "reuse": reuse(); reuse_text()
    elif a[0] == "check": sys.exit(1 if check() else 0)
    else: sys.exit(__doc__)
