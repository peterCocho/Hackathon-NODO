import pandas as pd

data = {
    "Producto": ["Harina Integral", "Azúcar Refinada", "Aceite Vegetal", "Levadura Seca", "Sal de Mar"],
    "Costo_Unitario": [1.20, 0.80, 2.50, 0.50, 0.30],
    "Precio_Venta": [1.40, 1.50, 3.00, 2.50, 0.90],
    "Stock_Actual": [5, 45, 12, 60, 100],
    "Stock_Minimo": [15, 20, 10, 15, 20],
    "Ventas_Mes_Anterior": [150, 200, 80, 120, 50],
    "Categoria": ["Insumos", "Insumos", "Insumos", "Aditivos", "Aditivos"]
}

df = pd.DataFrame(data)
df.to_csv("datos_pyme.csv", index=False)
print("Archivo 'datos_pyme.csv' creado con éxito.")