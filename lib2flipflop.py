# Copyright (c) 2026 CAD & Reliability Group, DAUIN, Polytechnic of Turin
#
# Authors:
# - Gabriele Belli  - gabriele.belli [at] studenti.polito.it or gb210403 [at] gmail.com
# - Filippo Carlone  - nome.cognome [at] studenti.polito.it or carlonefilippomm [at] gmail.com
# - Josie Esteban Rodriguez Condia  - josie.rodriguez [at] polito.it
# - Riccardo Cantoro  - riccardo.cantoro [at] polito.it
# - Matteo Sonza Reorda  - matteo.sonzareorda [at] polito.it
#
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
import gzip
import itertools
import os
import re
import warnings

# --------------------------------------------------------------------------
# Tokenizer + parser Liberty (minimale ma robusto a commenti, stringhe,
# continuazioni di riga e punti e virgola mancanti)
# --------------------------------------------------------------------------
TOKEN_RE = re.compile(r'''
    (?P<ws>\s+|\\\r?\n)                 # spazi e continuazioni di riga
  | (?P<comment>/\*.*?\*/|//[^\n]*)     # commenti
  | (?P<string>"(?:\\.|[^"\\])*")       # stringhe
  | (?P<punct>[{}();:,])                # punteggiatura
  | (?P<word>[^\s{}();:,"]+)            # identificatori / numeri / espressioni
''', re.VERBOSE | re.DOTALL)


def tokenize(text):
    toks = []
    for m in TOKEN_RE.finditer(text):
        kind = m.lastgroup
        if kind in ('ws', 'comment'):
            continue
        tok = m.group()
        if kind == 'string':
            toks.append(('str', tok[1:-1]))
        else:
            toks.append((kind, tok))
    return toks


class Group:
    __slots__ = ('type', 'args', 'attrs', 'children')

    def __init__(self, gtype, args):
        self.type = gtype
        self.args = args
        self.attrs = {}       # solo attributi semplici (nome : valore)
        self.children = []


def is_p(tok, ch):
    return tok[0] == 'punct' and tok[1] == ch


def parse(text):
    toks = tokenize(text)
    n = len(toks)
    root = Group('root', [])
    stack = [root]
    i = 0
    while i < n:
        tok = toks[i]
        if is_p(tok, '}'):
            if len(stack) > 1:
                stack.pop()
            i += 1
            continue
        if tok[0] == 'punct':
            i += 1
            continue

        name = tok[1]
        i += 1
        if i >= n:
            break
        nxt = toks[i]

        if is_p(nxt, ':'):                         # attributo semplice
            i += 1
            parts = []
            while i < n and not (is_p(toks[i], ';') or is_p(toks[i], '}')):

                if parts and i + 1 < n and (is_p(toks[i + 1], ':') or is_p(toks[i + 1], '(')):
                    break
                parts.append(toks[i][1])
                i += 1
            if i < n and is_p(toks[i], ';'):
                i += 1
            stack[-1].attrs[name] = ' '.join(parts)

        elif is_p(nxt, '('):                       # gruppo o attributo complesso
            i += 1
            args = []
            while i < n and not is_p(toks[i], ')'):
                if not is_p(toks[i], ','):
                    args.append(toks[i][1])
                i += 1
            i += 1                                 # salta ')'
            if i < n and is_p(toks[i], '{'):
                g = Group(name, args)
                stack[-1].children.append(g)
                stack.append(g)
                i += 1
            elif i < n and is_p(toks[i], ';'):
                i += 1                             # attributo complesso: ignorato
    return root


# --------------------------------------------------------------------------
# Analisi delle espressioni booleane Liberty
# --------------------------------------------------------------------------
IDENT = r'[A-Za-z_][\w\[\]\.]*'


def strip_outer_parens(e):
    while e.startswith('(') and e.endswith(')'):
        depth = 0
        for k, c in enumerate(e):
            depth += (c == '(') - (c == ')')
            if depth == 0 and k < len(e) - 1:
                return e                     # le parentesi esterne non racchiudono tutto
        e = e[1:-1]
    return e


def polarity(expr):
    """Ritorna ('alto'|'basso', pin) oppure (None, expr) se l'espressione e' complessa."""
    e = strip_outer_parens(expr.replace(' ', ''))
    m = re.fullmatch(r'!\(?(' + IDENT + r')\)?', e)          # !RN  /  !(RN)
    if m:
        return 'basso', m.group(1)
    m = re.fullmatch(r'\(?(' + IDENT + r')\)?\'', e)         # RN'  /  (RN)'
    if m:
        return 'basso', m.group(1)
    if re.fullmatch(IDENT, e):                                 # RN
        return 'alto', e
    return None, expr


# --------------------------------------------------------------------------
# Espressioni booleane Liberty -> AST (per riconoscere i mux)
# precedenza: ' e ! > ^ > & * spazio > | +
# --------------------------------------------------------------------------
BOOL_TOK_RE = re.compile(r"\s*([A-Za-z_][\w\[\]\.]*|[01]|[()!'&*|+^])")


def bool_tokens(s):
    toks, pos = [], 0
    s = s.strip()
    while pos < len(s):
        m = BOOL_TOK_RE.match(s, pos)
        if not m:
            raise ValueError(f'token non valido in {s!r}')
        toks.append(m.group(1))
        pos = m.end()
    return toks


def parse_bool(s):
    toks = bool_tokens(s)
    i = 0

    def peek():
        return toks[i] if i < len(toks) else None

    def take():
        nonlocal i
        i += 1
        return toks[i - 1]

    def starts_primary(t):
        return t is not None and (t in ('(', '!') or re.match(r'[A-Za-z_01]', t))

    def p_or():
        n = p_and()
        while peek() in ('|', '+'):
            take()
            n = ('or', n, p_and())
        return n

    def p_and():
        n = p_xor()
        while peek() in ('&', '*') or starts_primary(peek()):
            if peek() in ('&', '*'):
                take()
            n = ('and', n, p_xor())
        return n

    def p_xor():
        n = p_unary()
        while peek() == '^':
            take()
            n = ('xor', n, p_unary())
        return n

    def p_unary():
        if peek() == '!':
            take()
            return ('not', p_unary())
        n = p_primary()
        while peek() == "'":
            take()
            n = ('not', n)
        return n

    def p_primary():
        t = take() if peek() is not None else None
        if t == '(':
            n = p_or()
            if take() != ')':
                raise ValueError('parentesi non bilanciate')
            return n
        if t in ('0', '1'):
            return ('const', int(t))
        if t is None or not re.match(r'[A-Za-z_]', t):
            raise ValueError(f'atteso operando, trovato {t!r}')
        return ('var', t)

    ast = p_or()
    if i != len(toks):
        raise ValueError(f'token in eccesso in {s!r}')
    return ast


def bool_eval(n, env):
    op = n[0]
    if op == 'var':
        return env[n[1]]
    if op == 'const':
        return n[1]
    if op == 'not':
        return 1 - bool_eval(n[1], env)
    a, b = bool_eval(n[1], env), bool_eval(n[2], env)
    return {'and': a & b, 'or': a | b, 'xor': a ^ b}[op]


def bool_vars(n):
    if n[0] == 'var':
        return {n[1]}
    if n[0] == 'const':
        return set()
    return set().union(*(bool_vars(c) for c in n[1:]))


# --------------------------------------------------------------------------
# Utility
# --------------------------------------------------------------------------
POL_EN = {'alto': 'high', 'basso': 'low'}


def find_cells(node):
    for ch in node.children:
        if ch.type == 'cell':
            yield ch
        elif ch.type in ('root', 'library'):
            yield from find_cells(ch)


def iter_pins(node):
    for g in node.children:
        if g.type == 'pin':
            for name in g.args:
                yield name, g
        elif g.type in ('bus', 'bundle'):
            for name in g.args:
                yield name, g


def norm(s):
    return (s or '').replace(' ', '')


def family_pattern(cell_name):
    return re.sub(r'\d+$', '', cell_name) or cell_name


def signal(expr):
    """espressione di controllo -> {'pin', 'active', 'expr'}; None se assente"""
    if not expr:
        return None
    pol, pin = polarity(expr)
    if pol is None:
        return {'pin': None, 'active': None, 'expr': expr}
    return {'pin': pin, 'active': POL_EN[pol], 'expr': expr}


def mux_select(ast, ins):
    """se ast == S ? B : A (su esattamente 3 variabili) ritorna (A, B, S)"""
    if len(ins) != 3:
        return None
    envs = [dict(zip(ins, bits)) for bits in itertools.product((0, 1), repeat=3)]
    for s in ins:
        a, b = [p for p in ins if p != s]
        for x, y in ((a, b), (b, a)):
            if all(bool_eval(ast, e) == (e[y] if e[s] else e[x]) for e in envs):
                return x, y, s
    return None


def try_parse_bool(expr):
    try:
        return parse_bool(expr) if expr else None
    except ValueError:
        return None


def to_float(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


# --------------------------------------------------------------------------
# Estrazione celle sequenziali
# --------------------------------------------------------------------------
SEQ_TYPES = ('ff', 'ff_bank', 'latch', 'latch_bank', 'statetable')
SCAN_SIGNALS = ('test_scan_enable', 'test_scan_enable_inverted', 'test_scan_in',
                'test_scan_in_inverted', 'test_scan_out', 'test_scan_out_inverted',
                'test_scan_clock', 'test_scan_clock_a', 'test_scan_clock_b')


def scan_from_test_cell(cell):
    tc = next((g for g in cell.children if g.type == 'test_cell'), None)
    if tc is None:
        return None
    info = {}
    for name, p in iter_pins(tc):
        st = p.attrs.get('signal_type')
        if st in SCAN_SIGNALS:
            info[st] = name
    return info or {'test_cell': True}


def seq_entry(cell, g):
    name = cell.args[0] if cell.args else '?'
    pins = {n: p.attrs.get('direction') for n, p in iter_pins(cell)}
    outputs = {n: p.attrs.get('function') for n, p in iter_pins(cell)
               if p.attrs.get('direction') in ('output', 'inout')}
    e = {
        'cell': name,
        'family': family_pattern(name),
        'kind': g.type,
        'area': to_float(cell.attrs.get('area')),
        'dont_use': cell.attrs.get('dont_use', 'false').lower() == 'true',
        'pins': pins,
        'output_functions': outputs,
        'state_vars': list(g.args),
    }
    if g.type == 'statetable':
        e['statetable'] = g.attrs.get('table')
        return e

    is_latch = g.type.startswith('latch')
    var1 = norm(g.args[0]) if g.args else None
    var2 = norm(g.args[1]) if len(g.args) > 1 else None

    # clock / enable
    ck_expr = g.attrs.get('enable' if is_latch else 'clocked_on')
    ck = signal(ck_expr)
    if ck:
        if is_latch:
            ck['transparent_when'] = ck.pop('active')
        else:
            ck['edge'] = {'high': 'rising', 'low': 'falling', None: None}[ck.pop('active')]
    e['enable' if is_latch else 'clock'] = ck
    if not is_latch:
        e['clock2'] = signal(g.attrs.get('clocked_on_also'))

    # dato
    ns = g.attrs.get('data_in' if is_latch else 'next_state')
    e['next_state'] = ns
    pol, pin = polarity(ns) if ns else (None, None)
    e['next_state_simple'] = pol == 'alto'
    e['d_pin'] = pin if pol == 'alto' else None

    # uscite
    qn_forms = {var2, f'!{var1}', f"{var1}'", f'!({var1})', f"({var1})'"} - {None}
    e['q_pins'] = [n for n, f in outputs.items() if norm(f) == var1]
    e['qn_pins'] = [n for n, f in outputs.items() if norm(f) in qn_forms]

    # reset / set asincroni
    e['async_reset'] = signal(g.attrs.get('clear'))
    e['async_set'] = signal(g.attrs.get('preset'))
    e['clear_preset_var1'] = g.attrs.get('clear_preset_var1')
    e['clear_preset_var2'] = g.attrs.get('clear_preset_var2')

    # scan: test_cell se c'e', altrimenti dedotto da next_state = SE ? SI : D
    scan = scan_from_test_cell(cell)
    if not e['next_state_simple']:
        ast = try_parse_bool(ns)
        sel = mux_select(ast, sorted(bool_vars(ast))) if ast is not None else None
        if sel:
            d0, d1, s = sel
            si = (scan or {}).get('test_scan_in')
            if si in (d0, d1):                       # test_cell dice chi e' SI
                e['d_pin'] = d1 if si == d0 else d0
            else:
                e['d_pin'] = d0
            if scan is None:
                scan = {'test_scan_enable': s, 'test_scan_in': d1, 'data': d0,
                        'source': 'dedotto da next_state (assumendo SE attivo alto)'}
    e['scan'] = scan
    return e


def collect_sequential(root):
    out = []
    for cell in find_cells(root):
        for g in cell.children:
            if g.type in SEQ_TYPES:
                out.append(seq_entry(cell, g))
    return out


# --------------------------------------------------------------------------
# Mux 2:1
# --------------------------------------------------------------------------
def collect_muxes(root):
    out = []
    for cell in find_cells(root):
        if any(g.type in SEQ_TYPES for g in cell.children):
            continue
        pins = list(iter_pins(cell))
        ins = [n for n, p in pins if p.attrs.get('direction') == 'input']
        outs = [(n, p.attrs['function']) for n, p in pins
                if p.attrs.get('direction') == 'output' and 'function' in p.attrs]
        if len(ins) != 3 or len(outs) != 1:
            continue
        ast = try_parse_bool(outs[0][1])
        if ast is None or bool_vars(ast) != set(ins):
            continue
        for inverting, a in ((False, ast), (True, ('not', ast))):
            sel = mux_select(a, ins)
            if sel:
                out.append({'cell': cell.args[0], 'in_sel0': sel[0], 'in_sel1': sel[1],
                            'select': sel[2], 'out': outs[0][0], 'inverting': inverting,
                            'function': outs[0][1], 'area': to_float(cell.attrs.get('area')),
                            'dont_use': cell.attrs.get('dont_use', 'false').lower() == 'true'})
                break
    out.sort(key=lambda m: (m['inverting'], m['area'] if m['area'] is not None else 1e99, m['cell']))
    return out


# --------------------------------------------------------------------------
# Caricamento (con cache) + famiglie
# --------------------------------------------------------------------------
FAMILY_KEYS = ('kind', 'clock', 'd_pin', 'q_pins', 'qn_pins', 'async_reset', 'async_set', 'scan')
_CACHE = {}


def _families(sequential, cells):
    fams = {}
    for e in sequential:
        f = fams.setdefault(e['family'], {'cells': [], 'variants': []})
        f['cells'].append(e['cell'])
        sig = {k: e.get(k) for k in FAMILY_KEYS}
        if sig not in f['variants']:
            f['variants'].append(sig)
    for pat, f in fams.items():
        f['consistent'] = len(f['variants']) == 1
        f['also_matches'] = sorted(n for n in cells if pat in n and n not in f['cells'])
    return fams


def load(lib_path, tag=None):
    """tutti i dati di una libreria:
    {tag, file, library_name, sequential, muxes, cells, families}"""
    path = os.path.abspath(os.fspath(lib_path))
    key = (path, os.path.getmtime(path))
    if key not in _CACHE:
        opener = gzip.open if path.endswith('.gz') else open
        with opener(path, 'rt', encoding='utf-8', errors='replace') as f:
            root = parse(f.read())
        lib = next((g for g in root.children if g.type == 'library'), None)
        sequential = collect_sequential(root)
        cells = [c.args[0] for c in find_cells(root) if c.args]
        _CACHE[key] = {
            'file': path,
            'library_name': lib.args[0] if lib and lib.args else None,
            'sequential': sequential,
            'muxes': collect_muxes(root),
            'cells': cells,
            'families': _families(sequential, cells),
        }
    d = dict(_CACHE[key])
    d['tag'] = tag or d['library_name'] or os.path.splitext(os.path.basename(path))[0]
    return d


# --------------------------------------------------------------------------
# Funzioni che producono le variabili di Polaris
# --------------------------------------------------------------------------
def _is_plain_ff(e, include_scan, include_falling, include_dont_use):
    if e['kind'] != 'ff' or not e.get('q_pins') or not e.get('d_pin'):
        return False
    ck = e.get('clock') or {}
    if ck.get('pin') is None:
        return False
    if ck.get('edge') == 'falling' and not include_falling:
        return False
    if e.get('scan') and not include_scan:
        return False
    if not e['next_state_simple'] and not e.get('scan'):
        return False                      # next_state non riconosciuto (es. reset sincrono)
    if e['dont_use'] and not include_dont_use:
        return False
    return True


def _selected(lib, include_scan=False, include_falling=False, include_dont_use=True):
    """{pattern: [celle]} ordinato: pattern piu' lunghi prima"""
    sel = {}
    for e in lib['sequential']:
        if _is_plain_ff(e, include_scan, include_falling, include_dont_use):
            sel.setdefault(e['family'], []).append(e)
    return {p: sel[p] for p in sorted(sel, key=lambda p: (-len(p), p))}


def dff_families(lib_path, tag=None, include_scan=False, include_falling=False,
                 include_dont_use=True, warn=True):
    """[(pattern, clk, d, q, tag), ...]"""
    lib = load(lib_path, tag)
    out = []
    for pat, members in _selected(lib, include_scan, include_falling, include_dont_use).items():
        if warn:
            pinsets = {(e['clock']['pin'], e['d_pin'], e['q_pins'][0]) for e in members}
            if len(pinsets) > 1:
                warnings.warn(f'{pat}: pin diversi tra le celle {sorted(pinsets)}; uso il primo')
            others = lib['families'][pat]['also_matches']
            if others:
                warnings.warn(f'"{pat}" matcha anche: {", ".join(others)}')
        e = members[0]
        out.append((pat, e['clock']['pin'], e['d_pin'], e['q_pins'][0], lib['tag']))
    return out


def ff_type(lib_path, include_scan=False, include_falling=False, include_dont_use=True):
    """[pattern, ...] nello stesso ordine di dff_families()"""
    return list(_selected(load(lib_path), include_scan, include_falling, include_dont_use))


def ff_reset(lib_path, include_scan=False, include_falling=False, include_dont_use=True):
    """{pattern: {'reset': (pin, 'low'|'high') | None, 'set': (pin, ...) | None}}"""
    out = {}
    for pat, members in _selected(load(lib_path), include_scan, include_falling, include_dont_use).items():
        r, s = members[0].get('async_reset'), members[0].get('async_set')
        out[pat] = {'reset': (r['pin'], r['active']) if r else None,
                    'set': (s['pin'], s['active']) if s else None}
    return out


def mux_by_lib(lib_path, tag=None, prefer=None, include_dont_use=False):
    """{tag: (cell, in_sel0, in_sel1, sel, out)}: mux 2:1 non invertente di area minore.
    prefer='MUX2_X2' per forzare una cella specifica."""
    lib = load(lib_path, tag)
    cands = [m for m in lib['muxes'] if not m['inverting'] and (include_dont_use or not m['dont_use'])]
    if prefer:
        cands = [m for m in cands if m['cell'] == prefer]
    if not cands:
        warnings.warn(f"{lib['tag']}: nessun mux 2:1 trovato")
        return {}
    m = cands[0]                          # lib['muxes'] e' gia' ordinata per area
    return {lib['tag']: (m['cell'], m['in_sel0'], m['in_sel1'], m['select'], m['out'])}