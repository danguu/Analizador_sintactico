# Cálculo de FIRST, FOLLOW, PREDICT y tabla LL(1) a partir de una gramática textual.
# Formato esperado por línea:
#   NoTerminal -> alternativa1 | alternativa2 | ...
#   Cada alternativa: secuencia de símbolos separados por espacios.
#   Terminales entre comillas simples, ejemplo: 'if' '(' ')'
#   Epsilon: ε o EPS
# El primer NoTerminal será el símbolo inicial.

EPS = "ε"
END = "$"


def _trim(s):
    return s.strip()


def _is_terminal(sym):
    return len(sym) >= 2 and sym[0] == "'" and sym[-1] == "'"


def _is_epsilon(sym):
    return sym == EPS or sym.upper() == "EPS"


def _split_alts(rhs):
    alts = []
    buf = ""
    i = 0
    while i < len(rhs):
        if rhs[i] == "|":
            alts.append(buf.strip())
            buf = ""
            i += 1
            continue
        buf += rhs[i]
        i += 1
    if buf.strip():
        alts.append(buf.strip())
    return alts


def _split_seq(seq_str):
    # Divide una alternativa en símbolos:
    # - Si empieza con comilla simple, consume hasta la próxima comilla.
    # - Si no, consume racha de no-espacios.
    out = []
    i = 0
    n = len(seq_str)
    while i < n:
        # saltar espacios
        while i < n and seq_str[i].isspace():
            i += 1
        if i >= n:
            break
        if seq_str[i] == "'":
            j = i + 1
            while j < n and seq_str[j] != "'":
                j += 1
            if j >= n:
                raise ValueError("Terminal sin cerrar con comilla: " + seq_str[i:])
            out.append(seq_str[i : j + 1])  # incluye comillas
            i = j + 1
        else:
            j = i
            while j < n and not seq_str[j].isspace():
                j += 1
            out.append(seq_str[i:j])
            i = j
    return out


def leer_gramatica(texto):
    prods = {}  # dict NT -> lista de producciones (listas de símbolos)
    orden_nt = []
    for raw in texto.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "->" in line:
            lhs, rhs = line.split("->", 1)
        elif "::=" in line:
            lhs, rhs = line.split("::=", 1)
        else:
            raise ValueError(f"Producción inválida: {line}")
        A = lhs.strip()
        if A not in prods:
            prods[A] = []
            orden_nt.append(A)
        for alt in _split_alts(rhs):
            seq = _split_seq(alt)
            if len(seq) == 1 and _is_epsilon(seq[0]):
                prods[A].append([EPS])
            else:
                prods[A].append(seq)
    if not orden_nt:
        raise ValueError("Gramática vacía")
    start = orden_nt[0]
    return prods, start


# -----------------------------
# FIRST, FOLLOW, PREDICT, TABLE
# -----------------------------


def first_sets(prods):
    FIRST = {A: set() for A in prods}

    def first_seq(seq):
        out = set()
        all_eps = True
        for X in seq:
            if _is_epsilon(X):
                out.add(EPS)
                continue
            # Si X no es un no terminal declarado, trátalo como terminal
            if _is_terminal(X) or X not in prods:
                out.add(X)
                all_eps = False
                break
            for t in FIRST[X]:
                if t != EPS:
                    out.add(t)
            if EPS in FIRST[X]:
                all_eps = True
                continue
            else:
                all_eps = False
                break
        if all_eps:
            out.add(EPS)
        return out

    changed = True
    while changed:
        changed = False
        for A, alts in prods.items():
            before = len(FIRST[A])
            for alpha in alts:
                s = first_seq(alpha)
                FIRST[A].update(s)
            if len(FIRST[A]) != before:
                changed = True
    return FIRST


def follow_sets(prods, start, FIRST):
    FOLLOW = {A: set() for A in prods}
    FOLLOW[start].add(END)

    def first_of_seq(seq):
        out = set()
        for X in seq:
            if _is_epsilon(X):
                out.add(EPS)
                continue
            if _is_terminal(X) or X not in prods:
                out.add(X)
                return out, False
            out.update(t for t in FIRST[X] if t != EPS)
            if EPS in FIRST[X]:
                continue
            return out, False
        return out, True  # toda la secuencia puede ser ε

    changed = True
    while changed:
        changed = False
        for A, alts in prods.items():
            for alpha in alts:
                n = len(alpha)
                for i, B in enumerate(alpha):
                    if B in prods:  # solo no terminales
                        tail = alpha[i + 1 :] if i + 1 < n else []
                        f_tail, tail_nullable = first_of_seq(tail)
                        before = len(FOLLOW[B])
                        FOLLOW[B].update(f_tail - {EPS})
                        if tail_nullable or not tail:
                            FOLLOW[B].update(FOLLOW[A])
                        if len(FOLLOW[B]) != before:
                            changed = True
    return FOLLOW


def predict_sets(prods, FIRST, FOLLOW):
    PREDICT = {}
    for A, alts in prods.items():
        for idx, alpha in enumerate(alts):
            s = set()
            nullable = True
            for X in alpha:
                if _is_epsilon(X):
                    s.add(EPS)
                    continue
                if _is_terminal(X) or X not in prods:
                    s.add(X)
                    nullable = False
                    break
                s.update(t for t in FIRST[X] if t != EPS)
                if EPS in FIRST[X]:
                    nullable = True
                    continue
                else:
                    nullable = False
                    break
            if nullable or (len(alpha) == 1 and _is_epsilon(alpha[0])):
                s.update(FOLLOW[A])
            PREDICT[(A, idx)] = s
    return PREDICT


def ll1_table(prods, PREDICT):
    table = {A: {} for A in prods}
    conflicts = []
    for (A, idx), terms in PREDICT.items():
        for a in terms:
            if a == EPS:
                continue
            if a in table[A]:
                conflicts.append((A, a, table[A][a], idx))
            table[A][a] = idx
    return table, conflicts


def formatear_set(s):
    def key(x):
        if x == END:
            return (2, x)
        if _is_terminal(x):
            return (0, x)
        return (1, x)

    return "{" + ", ".join(sorted(s, key=key)) + "}"


def stringify_prod(A, alpha):
    rhs = " ".join(alpha)
    return f"{A} -> {rhs}"
