from indent_check import verificar_indentacion
from sintactico import analizar, OK_MSG


def correr_analisis(source: str):
    falla = verificar_indentacion(source)
    if falla:
        ln, col = falla
        return f"<{ln},{col}>Error sintactico: falla de indentacion"
    ok, err = analizar(source)
    if ok:
        return OK_MSG
    return err
