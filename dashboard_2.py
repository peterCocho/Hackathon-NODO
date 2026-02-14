import streamlit as st
import pandas as pd

# 1. CONFIGURACIÓN DE PÁGINA (Debe ser la primera línea de Streamlit)
st.set_page_config(
    page_title="SabIA - Inteligencia de Costos", 
    page_icon="💡", 
    layout="wide"
)

# ==========================================
# 2. FUNCIONES DE LÓGICA Y PROCESAMIENTO
# ==========================================

def limpiar_columna_numerica(serie):
    """Limpia símbolos de moneda y convierte a float para evitar TypeErrors"""
    return pd.to_numeric(
        serie.astype(str)
        .str.replace(r'[\$,\s]', '', regex=True)
        .str.replace(',', '.')
        , errors='coerce'
    ).fillna(0)

def procesar_datos_sabia(archivos):
    """Convierte la lista de archivos cargados en la Tabla Maestra"""
    datasets = {}
    # Nombres esperados de los archivos de Yocce
    mapeo_nombres = {
        'productos.csv': 'productos',
        'ventas.csv': 'ventas',
        'insumos.csv': 'insumos',
        'recetas.csv': 'recetas',
        'tiempos-produccion.csv': 'tiempos',
        'gastos-generales.csv': 'gastos'
    }

    try:
        # Cargar cada archivo que coincida con el nombre
        for subido in archivos:
            if subido.name in mapeo_nombres:
                datasets[mapeo_nombres[subido.name]] = pd.read_csv(subido, encoding='latin-1', sep=None, engine='python')

        if len(datasets) < 6:
            faltantes = set(mapeo_nombres.values()) - set(datasets.keys())
            st.warning(f"Faltan archivos por subir: {', '.join(faltantes)}")
            return None

        # --- LIMPIEZA DE DATOS (Nombres confirmados por el escáner de Pedro) ---
        datasets['insumos']['costo_unitario'] = limpiar_columna_numerica(datasets['insumos']['costo_unitario'])
        datasets['recetas']['cantidad'] = limpiar_columna_numerica(datasets['recetas']['cantidad'])
        datasets['productos']['precio_venta_actual'] = limpiar_columna_numerica(datasets['productos']['precio_venta_actual'])
        datasets['gastos']['monto_mensual'] = limpiar_columna_numerica(datasets['gastos']['monto_mensual'])
        datasets['ventas']['cantidad_vendida'] = limpiar_columna_numerica(datasets['ventas']['cantidad_vendida'])

        # --- UNIONES (JOINS) ---
        df_rece_insu = pd.merge(datasets['recetas'], datasets['insumos'], on='insumo_id')
        df_rece_insu['costo_linea'] = df_rece_insu['cantidad'] * df_rece_insu['costo_unitario']
        
        df_costo_dir = df_rece_insu.groupby('producto_id')['costo_linea'].sum().reset_index()
        df_costo_dir.rename(columns={'costo_linea': 'costo_insumos_total'}, inplace=True)

        maestra = pd.merge(datasets['productos'], df_costo_dir, on='producto_id', how='left').fillna(0)
        maestra = pd.merge(maestra, datasets['tiempos'], on='producto_id', how='left').fillna(0)

        # --- PRORRATEO DE GASTOS ---
        total_gastos = datasets['gastos']['monto_mensual'].sum()
        total_ventas = datasets['ventas']['cantidad_vendida'].sum()
        gasto_fijo_un = total_gastos / total_ventas if total_ventas > 0 else 0
        
        maestra['gasto_fijo_asignado'] = gasto_fijo_un
        maestra['costo_total_real'] = maestra['costo_insumos_total'] + maestra['gasto_fijo_asignado']
        maestra['margen_ganancia'] = maestra['precio_venta_actual'] - maestra['costo_total_real']
        maestra['rentabilidad_pct'] = (maestra['margen_ganancia'] / maestra['precio_venta_actual'].replace(0, 1)) * 100

        return maestra
    except Exception as e:
        st.error(f"Error procesando archivos: {e}")
        return None

# ==========================================
# 3. INTERFAZ: SIDEBAR (Panel de Control)
# ==========================================
with st.sidebar:
    st.title("⚙️ Configuración")
    st.markdown("---")
    
    st.header("📁 Carga de Archivos")
    archivos_uploader = st.file_uploader(
        "Sube los 6 CSVs del proyecto", 
        type="csv", 
        accept_multiple_files=True
    )
    
    st.markdown("---")
    st.header("🗺️ Roadmap SabIA")
    st.info("""
    - [x] Conexión de Datos
    - [x] Lógica de Costos (SENA)
    - [ ] **Visualización Pro** (Pedro)
    - [ ] Exportar PDF
    """)
    
    st.caption("Pedro | Fullstack & Data Analyst")

# ==========================================
# 4. CUERPO PRINCIPAL (Layout Asimétrico)
# ==========================================

col_principal, col_alertas = st.columns([3, 1])

with col_principal:
    st.title("💡 SabIA: Inteligencia de Costos para Pymes")
    st.markdown("---")

    if archivos_uploader and len(archivos_uploader) >= 6:
        df_final = procesar_datos_sabia(archivos_uploader)

        if df_final is not None:
            # KPIs
            k1, k2, k3 = st.columns(3)
            with k1:
                top_prod = df_final.loc[df_final['margen_ganancia'].idxmax(), 'nombre_producto']
                st.metric("🏆 Producto Estrella", top_prod)
            with k2:
                margen_prom = df_final['rentabilidad_pct'].mean()
                st.metric("💰 Margen Promedio", f"{margen_prom:.1f}%")
            with k3:
                gasto_un = df_final['gasto_fijo_asignado'].iloc[0]
                st.metric("🔌 Gasto Fijo/Unidad", f"${gasto_un:,.0f}")

            st.markdown("---")

            # Gráficos
            st.subheader("📊 Análisis de Rentabilidad por Producto")
            st.bar_chart(data=df_final, x="nombre_producto", y="margen_ganancia")

            st.subheader("⏳ Esfuerzo vs Recompensa (Tiempos)")
            st.scatter_chart(data=df_final, x="tiempo_total_min", y="margen_ganancia", color="nombre_producto")
    else:
        st.info("👋 **¡Bienvenido Pedro!** Por favor, carga los 6 archivos CSV en la barra lateral para activar SabIA.")
        st.image("https://images.unsplash.com/photo-1551288049-bebda4e38f71?auto=format&fit=crop&q=80&w=800", use_container_width=True)

# ==========================================
# 5. COLUMNA DE ALERTAS (Derecha)
# ==========================================
with col_alertas:
    st.header("🔔 Alertas")
    st.markdown("---")
    
    if 'df_final' in locals() and df_final is not None:
        baja_renta = df_final[df_final['rentabilidad_pct'] < 20]
        if not baja_renta.empty:
            for _, fila in baja_renta.iterrows():
                st.error(f"**{fila['nombre_producto']}**")
                st.caption(f"Rentabilidad: {fila['rentabilidad_pct']:.1f}%")
                st.progress(max(0, min(int(fila['rentabilidad_pct']), 100)) / 100)
        else:
            st.success("¡Márgenes saludables en todos los productos!")
    else:
        st.write("Sube los datos para ver las alertas de hoy.")