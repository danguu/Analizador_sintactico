from lexer_core import lexer
from tokens_def import SINGLE_OPS, MULTI_OPS, KEYWORDS

INV_SINGLE = {v: k for k, v in SINGLE_OPS.items()}
INV_MULTI = {v: k for k, v in MULTI_OPS.items()}


class Tok:
    __slots__ = ("tipo", "lex", "linea", "col")

    def __init__(self, tipo, lex, linea, col):
        self.tipo = tipo
        self.lex = lex
        self.linea = linea
        self.col = col

    def __repr__(self):
        return f"Tok({self.tipo},{self.lex},{self.linea},{self.col})"


def _parse_token_str(s):
    s = s.strip()
    assert s[0] == "<" and s[-1] == ">"
    inner = s[1:-1]

    parts, buf, q = [], "", False
    i = 0
    while i < len(inner):
        c = inner[i]
        if c == '"':
            q = not q
            buf += c
            i += 1
            continue
        if c == "," and not q:
            parts.append(buf)
            buf = ""
            i += 1
            continue
        buf += c
        i += 1
    parts.append(buf)

    # Casos emitidos por tu lexer
    if parts[0] in KEYWORDS:
        return Tok(parts[0], parts[0], int(parts[1]), int(parts[2]))
    if parts[0] == "id":
        return Tok("id", parts[1], int(parts[2]), int(parts[3]))
    if parts[0] == "tk_cadena":
        return Tok("tk_cadena", parts[1].strip('"'), int(parts[2]), int(parts[3]))
    if parts[0] == "tk_entero":
        return Tok("tk_entero", parts[1], int(parts[2]), int(parts[3]))

    tkn = parts[0]
    linea, col = int(parts[1]), int(parts[2])
    if tkn in INV_SINGLE:
        return Tok(tkn, INV_SINGLE[tkn], linea, col)
    if tkn in INV_MULTI:
        return Tok(tkn, INV_MULTI[tkn], linea, col)
    # fallback
    return Tok(tkn, tkn, linea, col)


def lex_to_tokens(source: str):
    """Convierte salida de tu lexer a lista de Tok."""
    ts = lexer(source)
    if ts is None:
        return None
    return [_parse_token_str(x) for x in ts]


def with_layout_tokens(source: str, base_tokens):
    """Inserta NEWLINE/INDENT/DEDENT como Python cuando no hay paréntesis abiertos."""
    lines = source.splitlines()
    # mapa de indent ancho por línea 1..N
    indents = {}
    for ln, raw in enumerate(lines, start=1):
        stripped = raw.lstrip("\t ")
        if stripped == "" or stripped.startswith("#"):
            continue
        leading = raw[: len(raw) - len(stripped)]
        width = 4 * len(leading) if "\t" in leading else len(leading)
        indents[ln] = width

    out = []
    stack = [0]
    i = 0
    n = len(base_tokens)
    cur_line = 1
    open_count = 0  # (), [], {}
    open_map = {"(": 1, ")": -1, "[": 1, "]": -1, "{": 1, "}": -1}

    def emit_newline_for(line_no):
        # Salta comentarios/líneas vacías ya filtradas arriba
        if line_no not in indents:
            return
        nonlocal stack
        cur = indents[line_no]
        top = stack[-1]
        if cur == top:
            out.append(Tok("NEWLINE", "\n", line_no, 1))
            return
        if cur == top + 4:
            out.append(Tok("NEWLINE", "\n", line_no, 1))
            stack.append(cur)
            out.append(Tok("INDENT", "<INDENT>", line_no, 1))
            return
        if cur < top:
            out.append(Tok("NEWLINE", "\n", line_no, 1))
            while stack and stack[-1] > cur:
                stack.pop()
                out.append(Tok("DEDENT", "<DEDENT>", line_no, 1))
            return
        # salto > 4: el check de indentación lo atrapará antes

    # Avanza por tokens y detecta cambios de línea
    while i < n:
        t = base_tokens[i]
        # Inserta NEWLINE/INDENT/DEDENT al empezar una nueva línea
        if t.linea > cur_line:
            # cerrar paréntesis abiertos evita NEWLINE significativo
            if open_count == 0:
                emit_newline_for(t.linea)
            cur_line = t.linea
        # actualiza open_count
        if t.lex in open_map:
            open_count += open_map[t.lex]
            if open_count < 0:
                open_count = 0
        out.append(t)
        i += 1

    # Final de archivo: emite NEWLINE y DEDENT restantes
    last_line = len(lines) if lines else 1
    out.append(Tok("NEWLINE", "\n", last_line, 1))
    while len(stack) > 1:
        stack.pop()
        out.append(Tok("DEDENT", "<DEDENT>", last_line, 1))
    return out
