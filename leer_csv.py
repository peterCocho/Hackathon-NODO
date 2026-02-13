import csv
import pandas as pd

df = pd.read_csv("datos_pyme.csv")
print(df.head())

# def leer_primeras_filas(ruta, n=5):
#   with open(ruta, newline="", encoding="utf-8") as f:
#     lector = csv.reader(f)
#     for i, fila in enumerate(lector):
#       if i >= n:
#         break
#       print(fila)

# if __name__ == "__main__":
#   ruta_archivo = input("Ruta del archivo CSV: ").strip()
#   leer_primeras_filas(ruta_archivo, n=5)
