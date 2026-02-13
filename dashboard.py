import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from ia_pyme import procesar_ia_pyme, calcular_impacto_economico, obtener_detalle_ajustes

# 1. Configuración profesional de la página
st.set_page_config(page_title="Copiloto Pyme", layout="wide")

st.title("SabIA ")
st.markdown("Transformando datos en acciones concretas.")

# 2. Sidebar para carga de datos (Evita bases de datos pesadas)
with st.sidebar:
    st.header("Carga de Datos")
    # Formato CSV/Excel definido en el MVP 
    uploaded_file = st.file_uploader("Sube el reporte de la Pyme (CSV/Excel)", type=["csv", "xlsx"])
    
    st.divider()
    st.info("Rol: Visualización (Pedro - Cúcuta, SENA)")

# 3. Lógica de Negocio Principal
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    
    # --- 1. Cálculos Dinámicos ---
    # Margen porcentual por producto
    df['Margen_%'] = ((df['Precio_Venta'] - df['Costo_Unitario']) / df['Precio_Venta']) * 100
    
    # Rentabilidad promedio
    rentabilidad_promedio = df['Margen_%'].mean()
    
    # Costos totales (Costo unitario * Ventas del mes)
    costos_totales = (df['Costo_Unitario'] * df['Ventas_Mes_Anterior']).sum()
    
    # Obtener las alertas y cálculos de impacto desde ia_pyme
    alertas, recomendaciones = procesar_ia_pyme(df)
    u_actual, u_proyectada, inc = calcular_impacto_economico(df)
    df_detalles = obtener_detalle_ajustes(df)
    total_alertas = len(alertas)

    # --- 2. Visualización de KPIs (Datos Reales) ---
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Rentabilidad Promedio", value=f"{rentabilidad_promedio:.1f}%")
    with col2:
        st.metric(label="Inversión Total (Costos)", value=f"${costos_totales:,.0f}")
    with col3:
        st.metric(label="Alertas Críticas", value=total_alertas, 
                  delta_color="inverse" if total_alertas > 0 else "normal")

    st.divider()

    # 5. Visualización de Inventario, Rentabilidad y Análisis Avanzado
    col_left, col_right = st.columns([2, 1]) # Damos más espacio a la izquierda para los gráficos
    
    with col_left:
        # --- 5.1 Control de Inventario ---
        st.subheader("📦 Control de Inventario: Actual vs. Mínimo")
        fig_inv = go.Figure(data=[
            go.Bar(name='Stock Actual', x=df['Producto'], y=df['Stock_Actual'], marker_color='#3366CC'),
            go.Bar(name='Mínimo Requerido', x=df['Producto'], y=df['Stock_Minimo'], marker_color='#FF9900')
        ])
        fig_inv.update_layout(barmode='group', template='plotly_white', height=400)
        st.plotly_chart(fig_inv, use_container_width=True)

        st.divider()

        # --- 5.2 Análisis de Rentabilidad Detallado ---
        st.subheader("📈 Margen de Ganancia por Producto")
        fig_margen = px.bar(df, x='Producto', y='Margen_%', text='Margen_%',
                            color='Margen_%', color_continuous_scale='RdYlGn', template='plotly_white')
        fig_margen.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        fig_margen.update_layout(yaxis=dict(ticksuffix="%", range=[0, df['Margen_%'].max() + 15]))
        st.plotly_chart(fig_margen, use_container_width=True)

        st.divider()

        # --- 5.3 NUEVO: Análisis de Salud del Portafolio (Scatter Plot) ---
        st.subheader("🔍 Volumen vs. Rentabilidad (Salud de Ventas)")
        st.markdown("Identifica productos que se venden mucho pero no dejan dinero.")
        fig_scat = px.scatter(df, x='Ventas_Mes_Anterior', y='Margen_%', text='Producto', 
                             size='Ventas_Mes_Anterior', color='Margen_%', 
                             color_continuous_scale='RdYlGn', template='plotly_white', height=500)
        st.plotly_chart(fig_scat, use_container_width=True)

        st.divider()

        # --- 5.4 NUEVO: Distribución de Costos (Treemap) ---
        st.subheader("🏗️ ¿Dónde está invertido tu dinero? (Costos Reales)")
        fig_tree = px.treemap(df, path=['Categoria', 'Producto'], values='Costo_Unitario',
                             color='Costo_Unitario', color_continuous_scale='Blues', template='plotly_white')
        st.plotly_chart(fig_tree, use_container_width=True)

        st.divider()

        # --- 5.5 Impacto Económico ---
        st.subheader("💰 Impacto Económico: Intuición vs. IA")
        fig_impacto = go.Figure(data=[
            go.Bar(name='Actual', x=['Situación Actual'], y=[u_actual], marker_color='#FF4B4B', text=[f"${u_actual:,.0f}"], textposition='auto'),
            go.Bar(name='Optimizado', x=['Con Copiloto IA'], y=[u_proyectada], marker_color='#00CC96', text=[f"${u_proyectada:,.0f}"], textposition='auto')
        ])
        fig_impacto.update_layout(title=f"Aumento potencial de ganancias: {inc:.1f}%", template='plotly_white')
        st.plotly_chart(fig_impacto, use_container_width=True)

        # --- 5.6 Tabla de Ajustes ---
        st.write("### 📋 Detalle de Ajustes Sugeridos")
        if not df_detalles.empty:
            st.dataframe(df_detalles, use_container_width=True, hide_index=True)
            st.caption("*Nota: El precio sugerido garantiza un margen mínimo del 25% sobre el costo real.*")
        else:
            st.success("Todos tus productos tienen márgenes saludables.")

    with col_right:
        # 6. EL CORAZÓN DEL PROYECTO: IA Accionable
        st.subheader("🧠 Recomendaciones de la IA")
        
        # Alertas de Inventario
        if alertas:
            st.write("**⚠️ Alertas Operativas**")
            for alerta in alertas:
                with st.expander(f"STOCK: {alerta['producto']}", expanded=True):
                    st.warning(alerta['mensaje'])
                    if st.button(alerta['accion'], key=f"btn_inv_{alerta['producto']}"):
                        st.success(f"Solicitud enviada para {alerta['producto']}")
        else:
            st.success("✅ Stock bajo control")

        st.divider()

        # Recomendaciones de Precio
        if recomendaciones:
            st.write("**💰 Oportunidades de Margen**")
            for rec in recomendaciones:
                with st.container():
                    st.info(f"**{rec['producto']}**")
                    st.write(rec['mensaje'])
                    st.write(rec['detalle'])
                    if st.button(rec['accion'], key=f"btn_price_{rec['producto']}"):
                        st.balloons()
                        st.success("Precio actualizado exitosamente.")
        else:
            st.success("✅ Precios optimizados")

# 7. Estado inicial cuando no hay datos
else:
    st.info("Por favor, sube un archivo para comenzar el análisis de productividad.")
    st.image("https://images.unsplash.com/photo-1551288049-bebda4e38f71?auto=format&fit=crop&q=80&w=800", 
             caption="Tu tablero de control para Pymes aparecerá aquí", use_container_width=True)

# 8. Roadmap (Para el Pitch de Gabriela)
st.sidebar.divider()
st.sidebar.write("**📍 Roadmap Futuro:**")
st.sidebar.write("- Integración WhatsApp Business")
st.sidebar.write("- Conexión real con ERP local")
st.sidebar.write("- Predicción de demanda avanzada")