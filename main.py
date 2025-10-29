from reporte import correr_analisis
from ll1_generar import generate_reports
import os

archivo = input("Dame el archivo para analizar: ").strip()

try:
    with open(archivo, "r", encoding="utf-8") as f:
        source = f.read()
except:  # noqa: E722
    print("No se pudo leer el archivo:", archivo)
    raise SystemExit(1)

salida = correr_analisis(source)
print(salida)

out_path = archivo.rsplit(".", 1)[0] + ".txt"
try:
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(salida if salida else "")
except:  # noqa: E722
    pass

# Genera reportes LL(1) si hay gramatica.txt
gram_path = "gramatica.txt"
if os.path.exists(gram_path):
    try:
        generate_reports(gram_path)
        print(
            "Reportes LL(1) generados: primeros.txt, siguientes.txt, predict.txt, tabla_ll1.txt"
        )
    except Exception as e:  # noqa: E722
        print("No se pudieron generar los reportes LL(1):", e)
