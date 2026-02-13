import pandas as pd

def procesar_ia_pyme(df):
    alertas = []
    recomendaciones = []
    
    for index, row in df.iterrows():
        # 1. Lógica de Inventario (Alerta)
        if row['Stock_Actual'] < row['Stock_Minimo']:
            alertas.append({
                "producto": row['Producto'],
                "mensaje": f"Stock crítico de {row['Producto']}. Quedan {row['Stock_Actual']} unidades (Mínimo: {row['Stock_Minimo']}).",
                "accion": "Generar Orden de Compra"
            })
            
        # 2. Lógica de Rentabilidad (Recomendación)
        margen = (row['Precio_Venta'] - row['Costo_Unitario']) / row['Precio_Venta']
        if margen < 0.20:  # Si el margen es menor al 20%
            nuevo_precio = row['Costo_Unitario'] / 0.75  # Sugerir precio para margen del 25%
            recomendaciones.append({
                "producto": row['Producto'],
                "mensaje": f"Margen bajo en {row['Producto']} ({margen:.1%}).",
                "detalle": f"Se recomienda subir el precio a ${nuevo_precio:.2f} para alcanzar un margen saludable.",
                "accion": "Actualizar Precio"
            })
            
    return alertas, recomendaciones

def calcular_impacto_economico(df):
    # 1. Utilidad Actual
    # Resuelve el problema de: "Venden, pero no saben si ganan" [cite: 8]
    utilidad_actual = ((df['Precio_Venta'] - df['Costo_Unitario']) * df['Ventas_Mes_Anterior']).sum()
    
    # 2. Utilidad Proyectada (Lógica de IA simple para el MVP [cite: 37])
    def aplicar_ajuste(row):
        margen = (row['Precio_Venta'] - row['Costo_Unitario']) / row['Precio_Venta']
        if margen < 0.20:
            precio_sugerido = row['Costo_Unitario'] / 0.75 # Margen objetivo 25%
            return (precio_sugerido - row['Costo_Unitario']) * row['Ventas_Mes_Anterior']
        return (row['Precio_Venta'] - row['Costo_Unitario']) * row['Ventas_Mes_Anterior']
    
    utilidad_proyectada = df.apply(aplicar_ajuste, axis=1).sum()
    incremento_porc = ((utilidad_proyectada - utilidad_actual) / utilidad_actual) * 100
    
    return utilidad_actual, utilidad_proyectada, incremento_porc


def obtener_detalle_ajustes(df):
    detalles = []
    
    for index, row in df.iterrows():
        margen_actual = (row['Precio_Venta'] - row['Costo_Unitario']) / row['Precio_Venta']
        
        if margen_actual < 0.20:
            precio_sugerido = row['Costo_Unitario'] / 0.75
            utilidad_actual = (row['Precio_Venta'] - row['Costo_Unitario']) * row['Ventas_Mes_Anterior']
            utilidad_nueva = (precio_sugerido - row['Costo_Unitario']) * row['Ventas_Mes_Anterior']
            ganancia_extra = utilidad_nueva - utilidad_actual
            
            detalles.append({
                "Producto": row['Producto'],
                "Precio Actual": f"${row['Precio_Venta']:.2f}",
                "Precio Sugerido (IA)": f"${precio_sugerido:.2f}",
                "Margen Anterior": f"{margen_actual:.1%}",
                "Margen Nuevo": "25.0%",
                "Ganancia Mensual Extra": f"+${ganancia_extra:,.0f}"
            })
            
    return pd.DataFrame(detalles)
