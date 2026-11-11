#!/usr/bin/env python3
"""Turn a column-aligned species | hosts | places table from a pdftotext -layout
text file into lists.txt rows (block|mite|hosts;|places;|status|note).

usage: layout_table.py TEXT START END BLOCK [--cols a,b] [--status N]
START/END are 1-based line numbers in TEXT. Columns are detected from the gap
positions that recur in most lines unless --cols gives the host and place start
offsets. Output goes to stdout for review before it is appended to lists.txt.
"""
import re, sys, collections

def segs(line):
    return [m.start() for m in re.finditer(r'(?:(?<=\s{2})|^)\S', line)]

NCOL = 2

BINOM = re.compile(r'^[A-Z][a-z]+ (\(|[a-z]|sp)')

def detect(lines):
    base = min((len(l) - len(l.lstrip()) for l in lines), default=0)
    s1, s2, s3 = [], [], []
    for l in lines:
        sg = segs(l)
        if len(sg) >= 3 and sg[0] - base <= 2 and BINOM.match(l.strip()):
            s1.append(sg[1]); s2.append(sg[2])
            if len(sg) >= 4: s3.append(sg[3])
    if not s1:
        return [40, 70]
    s1.sort(); s2.sort(); s3.sort()
    out = [s1[len(s1) // 2], s2[len(s2) // 2]]
    if NCOL > 2 and s3:
        out.append(s3[len(s3) // 2])
    return out

def joinc(old, new):
    if not new:
        return old
    if not old:
        return new
    if re.search(r'[,\-]\s*$|\b(and|&|of)\s*$', old) or not re.match(r'[A-Z0-9]', new):
        return old + ' ' + new
    return old + ', ' + new


def main():
    a = sys.argv[1:]
    text, start, end, block = a[0], int(a[1]), int(a[2]), a[3]
    cols = None
    if '--cols' in a:
        cols = [int(x) for x in a[a.index('--cols') + 1].split(',')]
    global NCOL
    if '--ncol' in a:
        NCOL = int(a[a.index('--ncol') + 1])
    lines = open(text, errors='replace').read().replace('\x0c', '').split('\n')[start - 1:end]
    lines = [l.rstrip() for l in lines if l.strip() and not re.fullmatch(r'\s*\d{1,3}\s*', l)]
    if cols is None:
        cols = detect(lines)
    lines = [l for l in lines if not re.match(r'^\s*Order\b[^|]*$', l[:cols[0]] if False else l) or len(segs(l)) > 1]
    c1, c2 = cols[0], cols[1]
    c3 = cols[2] if len(cols) > 2 else None
    recs = []
    base = min((len(l) - len(l.lstrip()) for l in lines), default=0)
    refs = [base, c1, c2] + ([c3] if c3 else [])
    for l in lines:
        cells = ['', '', '', '']
        for m in re.finditer(r'(?:(?<=\s{2})|^)\S.*?(?=\s{2,}|$)', l):
            k = min(range(len(refs)), key=lambda i: abs(m.start() - refs[i]))
            cells[k] += (' ' if cells[k] else '') + m.group(0).strip()
        n, h, p = cells[0], cells[1], cells[2]
        if n and (not recs or re.match(r'^(Family|Genus|Order|[A-Z][a-z]+ [a-z(]|[A-Z][a-z]+ sp)', n) and not re.match(r'^(Order)', n) or re.match(r'^(Family|Genus)', n)):
            if recs and re.match(r'^(Family|Genus)', n) and recs[-1]['n'] and not recs[-1]['h'] and not recs[-1]['p']:
                recs[-1]['n'] += ' ' + n
                recs[-1]['h'] += ' ' + h; recs[-1]['p'] += ' ' + p
                continue
            if re.match(r'^Genus', n) and recs and recs[-1]['n'].startswith('Family') and 'Genus' not in recs[-1]['n']:
                recs[-1]['n'] += ' ' + n; recs[-1]['h'] += ' ' + h; recs[-1]['p'] += ' ' + p
                continue
            recs.append({'n': n, 'h': h, 'p': p})
        elif recs:
            recs[-1]['n'] += (' ' + n) if n else ''
            recs[-1]['h'] = joinc(recs[-1]['h'], h)
            recs[-1]['p'] = joinc(recs[-1]['p'], p)
    fam = re.compile(r'^[A-Z][a-z]+idae$|^[A-Z][a-z]+oidea$')
    merged = []
    i = 0
    while i < len(recs):
        r = recs[i]
        nm = re.sub(r'^Family\s*:?\s*', '', r['n']).strip()
        if fam.match(nm) and i + 1 < len(recs) and not recs[i + 1]['h'] and (r['h'] or r['p']) and not fam.match(recs[i + 1]['n'].strip()):
            nx = recs[i + 1]
            merged.append({'n': nx['n'], 'h': r['h'], 'p': joinc(r['p'], nx['p'])})
            i += 2
            continue
        merged.append(r)
        i += 1
    recs = merged
    sys.stderr.write(f'columns {cols}, {len(recs)} records\n')
    for r in recs:
        if not r['n'] or re.match(r'^(Family|Order)\b', r['n']) and not r['h'] and not r['p'] and 'Genus' not in r['n']:
            continue
        name = re.sub(r'^(Order[^,]*,\s*)?', '', r['n'])
        name = re.sub(r'Family\s*:?\s*\w+\s*Genus\s*:?\s*', '', name).strip()
        name = re.sub(r'^Family\s*:?\s*', '', name)
        name = re.sub(r'\s+', ' ', name)
        hosts = '; '.join(x.strip() for x in re.split(r'[,;]', r['h']) if x.strip())
        places = '; '.join(x.strip() for x in re.split(r'[,;]', r['p']) if x.strip())
        print(f'{block}|{name}|{hosts}|{places}||')

main()
