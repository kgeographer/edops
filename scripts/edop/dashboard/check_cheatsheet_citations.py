"""Check the code citations in docs/design/dashboard/sandbox_cheatsheet.md.

Reads only. Extracts every `file:symbol` / `file:line` reference from the [code ...] and [doc ...]
tags and reports (1) symbols not found, (2) symbol:line pairs that drift by more than 6 lines,
(3) the text at each bare line number for manual review. Output is noisy (some words are read as
symbols); treat it as a list of leads, not verdicts. Run: python scripts/edop/dashboard/check_cheatsheet_citations.py
"""
import re, os, sys, collections
from pathlib import Path
ROOT=str(Path(__file__).resolve().parents[3])
MAP={"sandbox.html":"app/templates/sandbox.html","engine.py":"scripts/edop/areas/engine.py","routes_sandbox.py":"app/api/routes_sandbox.py",
"routes_common.py":"app/api/routes_common.py","seasonality.py":"app/db/seasonality.py","test_engine_contract.py":"tests/engine/test_engine_contract.py",
"test_area.py":"tests/test_area.py","test_live_server.py":"tests/test_live_server.py","reading-a-signature.md":"docsite/sandbox/reading-a-signature.md"}
cache={}
def lines(f):
    if f not in cache: cache[f]=open(os.path.join(ROOT,MAP[f]),encoding="utf-8").read().split("\n")
    return cache[f]
txt=open(ROOT+"/docs/design/dashboard/sandbox_cheatsheet.md",encoding="utf-8").read()
fre="|".join(re.escape(k) for k in MAP)
# split into per-tag chunks: any [ ... ] containing a known filename
chunks=re.findall(r"\[((?:code|doc)[^\]]*)\]",txt)
def defline(f,sym):
    pat=re.compile(r"(?:def|function|async function|class|const|let|var)\s+"+re.escape(sym)+r"\b|^\s*"+re.escape(sym)+r"\s*=|^"+re.escape(sym)+r"\s*[:=(]")
    hits=[i+1 for i,l in enumerate(lines(f)) if pat.search(l)]
    if not hits:
        hits=[i+1 for i,l in enumerate(lines(f)) if re.search(r"\b"+re.escape(sym)+r"\b",l)][:1]
        kind="mention"
    else: kind="def"
    return hits,kind
missing=[];drift=[];nums=[]
for ch in chunks:
    cur=None
    # tokenise: file markers and following items
    for m in re.finditer(r"("+fre+r")|([A-Za-z_][\w]*)(?::|\s)~?(\d+)(?:-(\d+))?|(?<![\w])~?(\d{2,5})(?:-(\d{2,5}))?(?![\w.])|([A-Za-z_][\w]*(?:/[\w]+)*)",ch):
        if m.group(1): cur=m.group(1); continue
        if cur is None: continue
        if m.group(2) and m.group(3):
            sym,l1=m.group(2),int(m.group(3))
            if sym in MAP or sym in ("code","doc"): continue
            h,k=defline(cur,sym)
            if not h: missing.append((cur,sym,ch[:70])); 
            elif min(abs(l1-x) for x in h)>6: drift.append((cur,sym,l1,h[:2],k))
            continue
        if m.group(5):
            l1=int(m.group(5)); nums.append((cur,l1,int(m.group(6)) if m.group(6) else None,ch[:60])); continue
        if m.group(7):
            sym=m.group(7)
            if sym in MAP or sym in ("code","doc","vs","and","live","inferred","comment","docstring","tests","at","the","from","in","of","on") or len(sym)<4 or sym.isdigit(): continue
            if not re.search(r"[_A-Z]|\d",sym) and sym.lower()==sym and len(sym)<9: continue   # plain words
            h,k=defline(cur,sym)
            if not h: missing.append((cur,sym,ch[:70]))
print("SYMBOLS NOT FOUND:",len(missing))
for x in sorted(set(missing)): print("  ",x)
print("\nSYMBOL:LINE DRIFT >6:",len(drift))
for x in drift: print("  ",x)
print("\nBARE LINE REFS:",len(nums))
seen=set()
for f,a,b,c in nums:
    if (f,a) in seen: continue
    seen.add((f,a))
    L=lines(f)
    t=L[a-1].strip()[:90] if 0<a<=len(L) else "!! BEYOND EOF (%d lines)"%len(L)
    print(f"  {f}:{a}{('-'+str(b)) if b else ''}  | {t}")
