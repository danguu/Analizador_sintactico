# Parser LL(1) manual. Sin parser.py ni librerías externas.
from bridge import lex_to_tokens, with_layout_tokens
from tokens_def import KEYWORDS

OK_MSG = "El analisis sintactico ha finalizado exitosamente."


class Parser:
    def __init__(self, tokens):
        self.t = tokens
        self.i = 0

    def cur(self):
        return self.t[self.i] if self.i < len(self.t) else None

    def adv(self):
        self.i += 1

    # === errores ===
    def error_lex(self, tok, esperados):
        if tok is None:
            ln = self.t[-1].linea if self.t else 1
            col = 1
            msg = (
                f'<{ln},{col}> Error sintactico: se encontro: "EOF"; se esperaba: '
                + ", ".join(f'"{e}"' for e in esperados)
                + "."
            )
            raise SyntaxError(msg)
        lex = tok.lex if tok.lex is not None else tok.tipo
        msg = (
            f'<{tok.linea},{tok.col}> Error sintactico: se encontro: "{lex}"; se esperaba: '
            + ", ".join(f'"{e}"' for e in esperados)
            + "."
        )
        raise SyntaxError(msg)

    def need_lex(self, *ops):
        tok = self.cur()
        if tok and tok.lex in ops:
            self.adv()
            return tok
        self.error_lex(tok, list(ops))

    def need_tipo(self, *tipos):
        tok = self.cur()
        if tok and tok.tipo in tipos:
            self.adv()
            return tok
        present = []
        for tp in tipos:
            if tp in KEYWORDS:
                present.append(tp)
            elif tp == "id":
                present.append("identificador")
            elif tp == "tk_entero":
                present.append("entero")
            elif tp == "tk_cadena":
                present.append("cadena")
            else:
                present.append(tp)
        self.error_lex(tok, present)

    # === entrada ===
    def file_input(self):
        while self.cur() and self.cur().tipo == "NEWLINE":
            self.adv()
        while self.cur() and self.cur().lex != "<eof>":
            self.stmt()
            while self.cur() and self.cur().tipo == "NEWLINE":
                self.adv()

    # stmt
    def stmt(self):
        tok = self.cur()
        if tok is None:
            self.error_lex(tok, ["declaracion"])
        if tok.lex in ("if", "while", "for", "def"):
            self.compound_stmt()
        else:
            self.simple_stmt()

    # simple_stmt := small_stmt (";" small_stmt)* [";"]
    def simple_stmt(self):
        self.small_stmt()
        while self.cur() and self.cur().lex == ";":
            self.adv()
            self.small_stmt()

    def small_stmt(self):
        tok = self.cur()
        if tok is None:
            self.error_lex(tok, ["sentencia"])
        if tok.lex == "return":
            self.adv()
            if self.cur() and self.cur().tipo not in ("NEWLINE", "DEDENT"):
                self.testlist()
            return
        if tok.lex in ("pass", "break", "continue"):
            self.adv()
            return
        if tok.tipo == "id":
            j = self.i + 1
            if j < len(self.t) and self.t[j].lex in ("=", ":"):
                self.need_tipo("id")
                if self.cur() and self.cur().lex == ":":
                    self.adv()
                    self.test()
                    if self.cur() and self.cur().lex == "=":
                        self.adv()
                        self.test()
                    return
                n_asg = 0
                while self.cur() and self.cur().lex == "=":
                    self.adv()
                    self.test()
                    n_asg += 1
                if n_asg == 0:
                    self.error_lex(self.cur(), ['"="'])
                return
        self.testlist()

    def compound_stmt(self):
        tok = self.cur()
        if tok.lex == "if":
            self.if_stmt()
            return
        if tok.lex == "while":
            self.while_stmt()
            return
        if tok.lex == "for":
            self.for_stmt()
            return
        if tok.lex == "def":
            self.funcdef()
            return
        self.error_lex(tok, ["if", "while", "for", "def"])

    def if_stmt(self):
        self.need_lex("if")
        self.test()
        self.need_lex(":")
        self.suite()
        while self.cur() and self.cur().lex == "elif":
            self.adv()
            self.test()
            self.need_lex(":")
            self.suite()
        if self.cur() and self.cur().lex == "else":
            self.adv()
            self.need_lex(":")
            self.suite()

    def while_stmt(self):
        self.need_lex("while")
        self.test()
        self.need_lex(":")
        self.suite()

    def for_stmt(self):
        self.need_lex("for")
        self.need_tipo("id")
        self.need_lex("in")
        self.testlist()
        self.need_lex(":")
        self.suite()

    def funcdef(self):
        self.need_lex("def")
        self.need_tipo("id")
        self.need_lex("(")
        if self.cur() and self.cur().tipo == "id":
            self.param()
            while self.cur() and self.cur().lex == ",":
                self.adv()
                if self.cur() and self.cur().lex == ")":
                    break
                self.param()
        self.need_lex(")")
        if self.cur() and self.cur().lex == "->":
            self.adv()
            self.test()
        self.need_lex(":")
        self.suite()

    def param(self):
        self.need_tipo("id")
        if self.cur() and self.cur().lex == ":":
            self.adv()
            self.test()
        if self.cur() and self.cur().lex == "=":
            self.adv()
            self.test()

    # suite := simple_stmt NEWLINE? | NEWLINE INDENT stmt+ DEDENT
    def suite(self):
        if self.cur() and self.cur().tipo == "NEWLINE":
            self.adv()
            self.need_tipo("INDENT")
            first = True
            while True:
                self.stmt()
                first = False
                if self.cur() and self.cur().tipo == "NEWLINE":
                    self.adv()
                if self.cur() and self.cur().tipo == "DEDENT":
                    self.adv()
                    break
                if self.cur() is None:
                    self.error_lex(self.cur(), ["DEDENT"])
            if first:
                self.error_lex(self.cur(), ["sentencia"])
        else:
            self.simple_stmt()

    # === Expresiones ===
    def testlist(self):
        self.test()
        while self.cur() and self.cur().lex == ",":
            self.adv()
            if self.cur() and self.cur().tipo in ("NEWLINE", "DEDENT"):
                break
            self.test()

    def test(self):
        self.or_test()

    def or_test(self):
        self.and_test()
        while self.cur() and self.cur().lex == "or":
            self.adv()
            self.and_test()

    def and_test(self):
        self.not_test()
        while self.cur() and self.cur().lex == "and":
            self.adv()
            self.not_test()

    def not_test(self):
        if self.cur() and self.cur().lex == "not":
            self.adv()
            self.not_test()
        else:
            self.comparison()

    def comparison(self):
        self.expr()
        while self.cur() and self.cur().lex in (
            "==",
            "!=",
            "<",
            ">",
            "<=",
            ">=",
            "in",
            "is",
        ):
            self.adv()
            if self.cur() and self.cur().lex == "not":
                self.adv()
                if self.cur() and self.cur().lex in ("in",):
                    self.adv()
            self.expr()

    def expr(self):
        self.term()
        while self.cur() and self.cur().lex in ("+", "-", "|", "^"):
            self.adv()
            self.term()

    def term(self):
        self.factor()
        while self.cur() and self.cur().lex in ("*", "//", "/", "%", "&"):
            self.adv()
            self.factor()

    def factor(self):
        if self.cur() and self.cur().lex in ("+", "-", "~"):
            self.adv()
            self.factor()
            return
        self.power()

    def power(self):
        self.atom_expr()
        if self.cur() and self.cur().lex == "**":
            self.adv()
            self.factor()

    def atom_expr(self):
        self.atom()
        while self.cur() and self.cur().lex in ("(", "[", "."):
            if self.cur().lex == "(":
                self.adv()
                if self.cur() and self.cur().lex != ")":
                    self.arglist()
                self.need_lex(")")
            elif self.cur().lex == "[":
                self.adv()
                if self.cur() and self.cur().lex != "]":
                    # primer elemento
                    self.test()
                    while self.cur() and self.cur().lex == ",":
                        comma_tok = self.cur()
                        self.adv()
                        if self.cur() and self.cur().lex == "]":
                            self.error_lex(comma_tok, ["]"])
                        self.test()
                self.need_lex("]")
            else:
                self.adv()
                self.need_tipo("id")

    def atom(self):
        tok = self.cur()
        if tok is None:
            self.error_lex(tok, ["identificador", "entero", "cadena", "(", "[", "{"])
        if tok.tipo in ("tk_entero", "tk_cadena"):
            self.adv()
            return
        if tok.tipo == "id":
            self.adv()
            return
        if tok.lex == "(":
            self.adv()
            if self.cur() and self.cur().lex != ")":
                self.testlist()
            self.need_lex(")")
            return
        if tok.lex == "[":
            # lista literal con prohibición de coma final
            self.adv()
            if self.cur() and self.cur().lex != "]":
                self.test()
                while self.cur() and self.cur().lex == ",":
                    comma_tok = self.cur()
                    self.adv()
                    if self.cur() and self.cur().lex == "]":
                        self.error_lex(comma_tok, ["]"])
                    self.test()
            self.need_lex("]")
            return
        if tok.lex == "{":
            self.dict_or_set()
            return
        self.error_lex(tok, ["identificador", "entero", "cadena", "(", "[", "{"])

    def dict_or_set(self):
        self.need_lex("{")
        if self.cur() and self.cur().lex == "}":
            self.adv()
            return
        self.test()
        if self.cur() and self.cur().lex == ":":
            self.adv()
            self.test()
            while self.cur() and self.cur().lex == ",":
                self.adv()
                if self.cur() and self.cur().lex == "}":
                    break
                self.test()
                self.need_lex(":")
                self.test()
            self.need_lex("}")
        else:
            while self.cur() and self.cur().lex == ",":
                self.adv()
                if self.cur() and self.cur().lex == "}":
                    break
                self.test()
            self.need_lex("}")

    def arglist(self):
        self.argument()
        while self.cur() and self.cur().lex == ",":
            self.adv()
            if self.cur() and self.cur().lex == ")":
                break
            self.argument()

    def argument(self):
        if self.cur() and self.cur().tipo == "id":
            j = self.i + 1
            if j < len(self.t) and self.t[j].lex == "=":
                self.need_tipo("id")
                self.need_lex("=")
                self.test()
                return
        self.test()


def analizar(source: str):
    base = lex_to_tokens(source)
    if base is None:
        return None, None
    tokens = with_layout_tokens(source, base)
    p = Parser(tokens)
    try:
        p.file_input()
        return True, None
    except SyntaxError as e:
        return False, str(e)
