from ll1_tools import (
    leer_gramatica,
    first_sets,
    follow_sets,
    predict_sets,
    ll1_table,
    formatear_set,
    stringify_prod,
    END,
)


def generate_reports(gram_path: str):
    with open(gram_path, "r", encoding="utf-8") as f:
        gtext = f.read()

    prods, start = leer_gramatica(gtext)
    FIRST = first_sets(prods)
    FOLLOW = follow_sets(prods, start, FIRST)
    PREDICT = predict_sets(prods, FIRST, FOLLOW)
    tabla, conflicts = ll1_table(prods, PREDICT)

    with open("primeros.txt", "w", encoding="utf-8") as f:
        for A in prods:
            f.write(f"FIRST({A}) = {formatear_set(FIRST[A])}\n")

    with open("siguientes.txt", "w", encoding="utf-8") as f:
        for A in prods:
            f.write(f"FOLLOW({A}) = {formatear_set(FOLLOW[A])}\n")

    with open("predict.txt", "w", encoding="utf-8") as f:
        for A, alts in prods.items():
            for idx, alpha in enumerate(alts):
                conj = PREDICT[(A, idx)]
                f.write(
                    f"PREDICT({stringify_prod(A, alpha)}) = {formatear_set(conj)}\n"
                )

    with open("tabla_ll1.txt", "w", encoding="utf-8") as f:
        terminals = set()
        for conj in PREDICT.values():
            for a in conj:
                if a != END and a.startswith("'") and a.endswith("'"):
                    terminals.add(a)
        cols = sorted(terminals) + [END]

        f.write("NT \\ a".ljust(20))
        for a in cols:
            f.write(a.ljust(20))
        f.write("\n")

        for A, alts in prods.items():
            f.write(A.ljust(20))
            for a in cols:
                cell = ""
                if a in tabla[A]:
                    idx = tabla[A][a]
                    cell = stringify_prod(A, alts[idx])
                f.write(cell.ljust(20))
            f.write("\n")

        if conflicts:
            f.write("\n# Conflictos LL(1):\n")
            for A, a, old_idx, new_idx in conflicts:
                f.write(f"# conflicto en M[{A},{a}]: {old_idx} vs {new_idx}\n")


if __name__ == "__main__":
    path = input("Ruta de gramatica.txt: ").strip()
    generate_reports(path)
    print(
        "Reportes generados: primeros.txt, siguientes.txt, predict.txt, tabla_ll1.txt"
    )
