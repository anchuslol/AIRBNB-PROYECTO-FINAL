import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
import traceback

st.set_page_config(
    page_title="Panel de Análisis de mercado inmobiliario (AirBnb)",
    page_icon="🏠📊",
    layout="wide"
)

st.title("🏠📊 Panel de Análisis de mercado inmobiliario (AirBnb)")
st.markdown("""
Este panel te permite explorar datos del mercado inmobiliario en Valencia, Málaga, Madrid y Barcelona para su inversión.
Utiliza los filtros y selectores en la barra lateral para personalizar tu análisis.
""")

@st.cache_data(ttl=3600)
def load_data():
    try:
        df_valencia = pd.read_csv('data/Valencia_limpio.csv')
        df_inmobiliario = pd.read_csv("data/valencia_vivienda_limpio.csv")
        df_delincuencia = pd.read_csv("data/crimenValencia.csv", sep=';')
        df_barcelona = pd.read_csv("data/barcelona_limpio_completo.csv")
        df_barcelona_inversores = pd.read_csv("data/barcelona_inversores.csv")
        return df_valencia, df_inmobiliario, df_delincuencia,df_barcelona, df_barcelona_inversores
    except Exception as e:
        st.error(f"Error al cargar los datos: {e}")
        st.text(traceback.format_exc())
        return None, None, None

df_valencia, df_inmobiliario, df_delincuencia,df_barcelona, df_barcelona_inversores = load_data()

# Preprocesamiento básico y filtros
if df_valencia is not None and df_inmobiliario is not None:
    if 'price' in df_valencia.columns:
        df_valencia['price'] = df_valencia['price'].astype(float)
    if 'precio' in df_inmobiliario.columns:
        precio_m2_valencia = df_inmobiliario['precio'].mean()
    else:
        precio_m2_valencia = 2000  # fallback
    average_m2 = 70
    df_valencia['annual_income'] = df_valencia['price'] * df_valencia['days_rented']
    df_valencia['estimated_property_value'] = precio_m2_valencia * average_m2
    df_valencia['ROI (%)'] = (df_valencia['annual_income'] / df_valencia['estimated_property_value']) * 100
    gastos_anuales = 3000
    df_valencia['net_annual_income'] = df_valencia['annual_income'] - gastos_anuales
    df_valencia['Net ROI (%)'] = (df_valencia['net_annual_income'] / df_valencia['estimated_property_value']) * 100

    st.sidebar.header("Filtros")

    
    # Filtro por ciudad
ciudades = ['Valencia', 'Malaga', 'Madrid', 'Barcelona']

if 'city' in df_valencia.columns:
    ciudad_seleccionada = st.sidebar.selectbox("Selecciona ciudad", ciudades)

    # Selecciona el dataframe según la ciudad
    if ciudad_seleccionada.lower() == 'valencia':
        df_ciudad = df_valencia
    elif ciudad_seleccionada.lower() == 'barcelona':
        df_ciudad = df_barcelona
    elif ciudad_seleccionada.lower() == 'malaga':
        try:
            df_malaga = pd.read_csv("../data/malaga_limpio.csv")
        except Exception as e:
            st.warning("No se pudo cargar el dataset de Málaga.")
            st.stop()
        df_ciudad = df_malaga
    elif ciudad_seleccionada.lower() == 'madrid':
        try:
            df_madrid = pd.read_csv("../data/madrid_limpio.csv")
        except Exception as e:
            st.warning("No se pudo cargar el dataset de Madrid.")
            st.stop()
        df_ciudad = df_madrid
    else:
        st.warning("Ciudad no reconocida.")
        st.stop()

    # Filtro por barrios
    if 'neighbourhood' in df_ciudad.columns:
        barrios = sorted(df_ciudad['neighbourhood'].dropna().unique())
        selected_barrios = st.sidebar.multiselect("Selecciona barrios", options=barrios, default=barrios)
        df_ciudad = df_ciudad[df_ciudad['neighbourhood'].isin(selected_barrios)]
        if df_ciudad.empty:
            st.warning("No hay datos para los barrios seleccionados en la ciudad.")
            st.stop()
    else:
        st.sidebar.warning("No se encontró la columna 'neighbourhood' en los datos de la ciudad seleccionada.")
        st.stop()

else:
    st.sidebar.warning("No se encontró la columna 'city' en los datos. Mostrando todos los datos.")
    barrios = sorted(df_valencia['neighbourhood'].dropna().unique())
    selected_barrios = st.sidebar.multiselect("Selecciona barrios", options=barrios, default=barrios)
    df_valencia = df_valencia[df_valencia['neighbourhood'].isin(selected_barrios)]
    if df_valencia.empty:
        st.warning("No hay datos para los barrios seleccionados.")
        st.stop()

# Definir pestañas por ciudad usando la ciudad seleccionada del filtro
tabs_por_ciudad = {
    "valencia": [
        "📊 Resumen General",
        "🏠 Precios de Vivienda",
        "💸 Rentabilidad por Barrio",
        "📈 Competencia y Demanda",
        "🔍 Análisis Avanzado",
        "📝 Conclusiones"
    ],
    "barcelona": [
        "📊 Barcelona General",
        "🏠 Barcelona de Vivienda",
        "💸 Rentabilidad por Barrio",
       # "📈 Competencia y Demanda",
       # "🔍 Análisis Avanzado",
       # "📝 Conclusiones"
    ],
    "madrid": [
        "📊 Madrid General",
        "🏠 Madrid de Vivienda",
        "💸 Rentabilidad por Barrio",
        "📈 Competencia y Demanda",
        "🔍 Análisis Avanzado",
        "📝 Conclusiones"
    ],
    "malaga": [
        "📊 Málaga General",
        "🏠 Málaga de Vivienda",
        "💸 Rentabilidad por Barrio",
        "📈 Competencia y Demanda",
        "🔍 Análisis Avanzado",
        "📝 Conclusiones"
    ]
}

# Convertir la ciudad seleccionada a minúsculas para buscar en el diccionario
# Convertir la ciudad seleccionada a minúsculas para buscar en el diccionario
ciudad_actual = ciudad_seleccionada.lower()
pestañas = tabs_por_ciudad.get(ciudad_actual, [])

if not pestañas:
    st.warning(f"No hay pestañas definidas para la ciudad '{ciudad_seleccionada}'.")
    st.stop()

main_tabs = st.tabs(pestañas)

# Mostrar contenido básico para testear acceso a pestañas (debug)
for i, tab in enumerate(main_tabs):
    with tab:
        st.write("")
      


# ------------------ Pestaña 1: Resumen General ------------------
if len(main_tabs) > 0:
    with main_tabs[0]:
        if ciudad_actual == "valencia":
            st.subheader("Resumen General del Mercado Inmobiliario")
        
            col1, col2, col3 = st.columns(3)
            col1.metric("Nº de anuncios", len(df_ciudad))
            col2.metric("ROI Neto medio (%)", f"{df_ciudad['Net ROI (%)'].mean():.2f}")
            col3.metric("Precio medio alquiler (€)", f"{df_ciudad['price'].mean():.2f}")

            # KDE ROI Bruto y Neto
            st.markdown("#### Distribución de ROI Bruto y Neto (%)")
            if len(df_ciudad) > 1:
                fig, ax = plt.subplots(figsize=(10, 5))
                sns.kdeplot(df_ciudad['ROI (%)'], fill=True, label='ROI Bruto (%)', color='skyblue', bw_adjust=0.7, clip=(0, 50), ax=ax)
                sns.kdeplot(df_ciudad['Net ROI (%)'], fill=True, label='ROI Neto (%)', color='orange', bw_adjust=0.7, clip=(0, 50), ax=ax)
                ax.set_title('Distribución de ROI Bruto y Neto')
                ax.set_xlabel('ROI (%)')
                ax.set_ylabel('Densidad')
                ax.set_xlim(0, 50)
                ax.legend()
                st.pyplot(fig)
            else:
                st.info("No hay suficientes datos para mostrar la distribución de ROI.")

        elif ciudad_actual == "barcelona":
            st.info("Si la ciudad es Barcelona añadir código aquí")

        elif ciudad_actual == "malaga":
            st.info("Si la ciudad es Málaga añadir código aquí")

        elif ciudad_actual == "madrid":
            st.subheader("📊 Resumen General del Mercado Inmobiliario en Madrid")
            
            # Métricas clave
            col1, col2, col3 = st.columns(3)
            col1.metric("Nº de anuncios", len(df_ciudad))
            col2.metric("Precio medio €/m²", f"{df_ciudad['price_per_m2_jun2025'].mean():.2f}")
            col3.metric("Rentabilidad media (€)", f"{df_ciudad['estimated_revenue_l365d'].mean():.2f}")

            # Distribución de rentabilidad estimada
            st.markdown("#### Distribución de Rentabilidad Estimada (€ / año)")
            if len(df_ciudad) > 1:
                fig, ax = plt.subplots(figsize=(10, 5))
                sns.kdeplot(df_ciudad['estimated_revenue_l365d'], fill=True, color='skyblue', bw_adjust=0.7, ax=ax)
                ax.set_title('Distribución de Rentabilidad Estimada')
                ax.set_xlabel('Rentabilidad (€)')
                ax.set_ylabel('Densidad')
                st.pyplot(fig)
            else:
                st.info("No hay suficientes datos para mostrar la distribución de rentabilidad.")

        else:
            st.info("No hay datos para mostrar en esta pestaña.")
else:
    st.warning("No hay pestañas disponibles para mostrar contenido.")


# ------------------ Pestaña 2: Precios de Vivienda ------------------
with main_tabs[1]:
    if ciudad_actual.lower() == "valencia":
        st.subheader("Precios de Vivienda por Barrio")
    
        if 'precio' in df_inmobiliario.columns:
            barrio_caros = df_inmobiliario.groupby('neighbourhood')['precio'].mean().reset_index()
            barrio_caros = barrio_caros.sort_values(by='precio', ascending=False).head(15)
            if not barrio_caros.empty:
                fig_precio = px.bar(
                    barrio_caros,
                    x='precio',
                    y='neighbourhood',
                    orientation='h',
                    labels={'precio': 'Precio medio m2 de compra (€)', 'neighbourhood': 'Barrio'},
                    title='Top 15 barrios más caros por precio medio m2 de compra'
                )
                st.plotly_chart(fig_precio, use_container_width=True)
            else:
                st.info("No hay datos de precios de vivienda para mostrar.")
        else:
            st.info("No hay datos de precios de vivienda para mostrar.")
    elif ciudad_actual.lower() == "barcelona":
        st.info("Si la ciudad es barcelona añadir codigo aqui")
    elif ciudad_actual.lower() == "malaga":
        st.info("Si la ciudad es malaga añadir codigo aqui")
    elif ciudad_actual.lower() == "madrid":
        st.subheader("🏠 Precios de Vivienda por Barrio en Madrid")
            
            if 'price_per_m2_jun2025' in df_ciudad.columns:
                barrio_caros = df_ciudad.groupby('neighbourhood')['price_per_m2_jun2025'].mean().reset_index()
                barrio_caros = barrio_caros.sort_values(by='price_per_m2_jun2025', ascending=False).head(15)
                if not barrio_caros.empty:
                    fig_precio = px.bar(
                        barrio_caros,
                        x='price_per_m2_jun2025',
                        y='neighbourhood',
                        orientation='h',
                        labels={'price_per_m2_jun2025': 'Precio medio €/m²', 'neighbourhood': 'Barrio'},
                        title='Top 15 barrios más caros por precio medio €/m²'
                    )
                    st.plotly_chart(fig_precio, use_container_width=True)
                else:
                    st.info("No hay datos de precios de vivienda para mostrar.")
            else:
                st.info("No hay datos de precios de vivienda para mostrar.")

    else:
        st.info("No hay datos para mostrar en esta pestaña.")

# ------------------ Pestaña 3: Rentabilidad por Barrio ------------------
if len(main_tabs) > 2:
    with main_tabs[2]:
        if ciudad_actual == "valencia":
            st.subheader("Rentabilidad por Barrio")

            if not df_ciudad.empty:
                # ROI neto por barrio
                roi_barrio = df_ciudad.groupby('neighbourhood')['Net ROI (%)'].mean().sort_values(ascending=False).head(15)
                if not roi_barrio.empty:
                    fig_roi = px.bar(
                        roi_barrio,
                        x=roi_barrio.values,
                        y=roi_barrio.index,
                        orientation='h',
                        labels={'x': 'ROI Neto (%)', 'y': 'Barrio'},
                        title='Top 15 barrios por ROI Neto (%)'
                    )
                    st.plotly_chart(fig_roi, use_container_width=True)
                else:
                    st.info("No hay datos de ROI Neto para mostrar.")

                # ROI bruto por barrio
                roi_barrio_bruto = df_ciudad.groupby('neighbourhood')['ROI (%)'].mean().sort_values(ascending=False).head(15)
                if not roi_barrio_bruto.empty:
                    fig_roi_bruto = px.bar(
                        roi_barrio_bruto,
                        x=roi_barrio_bruto.values,
                        y=roi_barrio_bruto.index,
                        orientation='h',
                        labels={'x': 'ROI Bruto (%)', 'y': 'Barrio'},
                        title='Top 15 barrios por ROI Bruto (%)'
                    )
                    st.plotly_chart(fig_roi_bruto, use_container_width=True)
                else:
                    st.info("No hay datos de ROI Bruto para mostrar.")
            else:
                st.info("No hay datos para mostrar en esta pestaña.")

        elif ciudad_actual == "barcelona":
            st.info("Si la ciudad es Barcelona añadir código aquí")

        elif ciudad_actual == "malaga":
            st.info("Si la ciudad es malaga añadir código aquí")

        elif ciudad_actual == "madrid":
            st.subheader("💸 Rentabilidad por Barrio en Madrid")

            if not df_ciudad.empty:
                rentabilidad_barrio = df_ciudad.groupby('neighbourhood')['estimated_revenue_l365d'].mean().sort_values(ascending=False).head(15)
                if not rentabilidad_barrio.empty:
                    fig_rentabilidad = px.bar(
                        rentabilidad_barrio,
                        x=rentabilidad_barrio.values,
                        y=rentabilidad_barrio.index,
                        orientation='h',
                        labels={'x': 'Rentabilidad Estimada (€)', 'y': 'Barrio'},
                        title='Top 15 barrios por Rentabilidad Estimada (€)'
                    )
                    st.plotly_chart(fig_rentabilidad, use_container_width=True)
                else:
                    st.info("No hay datos de rentabilidad estimada para mostrar.")
            else:
                st.info("No hay datos para mostrar en esta pestaña.")

        else:
            st.info("No hay datos para mostrar en esta pestaña.")
else:
     st.warning("No hay pestañas disponibles para mostrar contenido.")


# ------------------ Pestaña 4: Competencia y Demanda ------------------
if len(main_tabs) > 3:
    with main_tabs[3]:
        if ciudad_actual == "valencia":
            st.subheader("Competencia y Demanda por Barrio")

            if not df_ciudad.empty:
                # Competencia por barrio
                competencia_por_barrio = df_ciudad.groupby('neighbourhood')['id'].count().reset_index().rename(columns={'id': 'n_anuncios'})
                top_comp = competencia_por_barrio.sort_values(by='n_anuncios', ascending=False).head(15)
                if not top_comp.empty:
                    fig_comp = px.bar(
                        top_comp,
                        x='n_anuncios',
                        y='neighbourhood',
                        orientation='h',
                        labels={'n_anuncios': 'Nº de anuncios', 'neighbourhood': 'Barrio'},
                        title='Top 15 barrios con más competencia (nº de anuncios)'
                    )
                    st.plotly_chart(fig_comp, use_container_width=True)
                else:
                    st.info("No hay datos de competencia para mostrar.")

                # Anuncios activos (>30 días alquilados/año)
                if 'days_rented' in df_ciudad.columns:
                    activos = df_ciudad[df_ciudad['days_rented'] > 30]
                    competencia_activa = activos.groupby('neighbourhood')['id'].count().reset_index().rename(columns={'id': 'n_anuncios_activos'})
                    top_activos = competencia_activa.sort_values(by='n_anuncios_activos', ascending=False).head(15)
                    if not top_activos.empty:
                        fig_activos = px.bar(
                            top_activos,
                            x='n_anuncios_activos',
                            y='neighbourhood',
                            orientation='h',
                            labels={'n_anuncios_activos': 'Nº de anuncios activos', 'neighbourhood': 'Barrio'},
                            title='Top 15 barrios con más anuncios activos (>30 días alquilados/año)'
                        )
                        st.plotly_chart(fig_activos, use_container_width=True)
                    else:
                        st.info("No hay datos de anuncios activos para mostrar.")
                else:
                    st.info("No hay datos de días alquilados para mostrar anuncios activos.")
            else:
                st.info("No hay datos para mostrar en esta pestaña.")

        elif ciudad_actual == "barcelona":
            st.info("Si la ciudad es Barcelona añadir código aquí")
        elif ciudad_actual == "malaga":
            st.info("Si la ciudad es malaga añadir código aquí")
        elif ciudad_actual == "madrid":
            st.subheader("📈 Competencia y Demanda por Barrio en Madrid")

            if not df_ciudad.empty:
                # Competencia por barrio
                competencia_por_barrio = df_ciudad.groupby('neighbourhood')['id'].count().reset_index().rename(columns={'id': 'n_anuncios'})
                top_comp = competencia_por_barrio.sort_values(by='n_anuncios', ascending=False).head(15)
                if not top_comp.empty:
                    fig_comp = px.bar(
                        top_comp,
                        x='n_anuncios',
                        y='neighbourhood',
                        orientation='h',
                        labels={'n_anuncios': 'Nº de anuncios', 'neighbourhood': 'Barrio'},
                        title='Top 15 barrios con más competencia (nº de anuncios)'
                    )
                    st.plotly_chart(fig_comp, use_container_width=True)
                else:
                    st.info("No hay datos de competencia para mostrar.")

                # Anuncios activos (>30 días alquilados/año)
                if 'days_rented' in df_ciudad.columns:
                    activos = df_ciudad[df_ciudad['days_rented'] > 30]
                    competencia_activa = activos.groupby('neighbourhood')['id'].count().reset_index().rename(columns={'id': 'n_anuncios_activos'})
                    top_activos = competencia_activa.sort_values(by='n_anuncios_activos', ascending=False).head(15)
                    if not top_activos.empty:
                        fig_activos = px.bar(
                            top_activos,
                            x='n_anuncios_activos',
                            y='neighbourhood',
                            orientation='h',
                            labels={'n_anuncios_activos': 'Nº de anuncios activos', 'neighbourhood': 'Barrio'},
                            title='Top 15 barrios con más anuncios activos (>30 días alquilados/año)'
                        )
                        st.plotly_chart(fig_activos, use_container_width=True)
                    else:
                        st.info("No hay datos de anuncios activos para mostrar.")
                else:
                    st.info("No hay datos de días alquilados para mostrar anuncios activos.")
            else:
                st.info("No hay datos para mostrar en esta pestaña.")

        else:
            st.info("No hay datos para mostrar en esta pestaña.")
else:
     st.warning("No hay pestañas disponibles para mostrar contenido.")


# ------------------ Pestaña 5: Análisis Avanzado ------------------
if len(main_tabs) > 4:
    with main_tabs[4]:
        if ciudad_actual.lower() == "valencia":
            st.subheader("Análisis Avanzado")
        
            if not df_valencia.empty:
                # Relación entre precio medio de alquiler y ROI neto por barrio
                st.markdown("#### Relación entre precio medio de alquiler y ROI neto por barrio")
                if 'city' in df_valencia.columns and df_valencia['city'].str.lower().nunique() == 1 and df_valencia['city'].str.lower().iloc[0] == 'valencia':
                    if 'price' in df_valencia.columns and 'Net ROI (%)' in df_valencia.columns:
                        fig_val = px.scatter(
                            df_valencia,
                            x='price',
                            y='Net ROI (%)',
                            color='neighbourhood',
                            hover_data=['neighbourhood'],
                            opacity=0.6,
                            labels={'price': 'Precio alquiler (€)', 'Net ROI (%)': 'ROI Neto (%)', 'neighbourhood': 'Barrio'},
                            title='Relación entre precio de alquiler y ROI neto por barrio (Valencia)'
                        )
                        fig_val.update_traces(marker=dict(size=10, line=dict(width=1, color='DarkSlateGrey')))
                        fig_val.update_layout(
                            legend_title_text='Barrio',
                            showlegend=False,
                            height=500,
                            margin=dict(l=40, r=40, t=60, b=40)
                        )
                        st.plotly_chart(fig_val, use_container_width=True)
                    else:
                        st.info("No hay datos suficientes para mostrar el gráfico de dispersión para Valencia.")
                else:
                    df_barrio = df_valencia.groupby('neighbourhood').agg({'price': 'mean', 'Net ROI (%)': 'mean'}).reset_index()
                    if not df_barrio.empty:
                        fig_scatter = px.scatter(
                            df_barrio,
                            x='price',
                            y='Net ROI (%)',
                            text='neighbourhood',
                            labels={'price': 'Precio medio alquiler (€)', 'Net ROI (%)': 'ROI Neto (%)'},
                            title='Precio medio de alquiler vs ROI Neto por barrio'
                        )
                        fig_scatter.update_traces(marker=dict(size=12, color='royalblue', line=dict(width=1, color='DarkSlateGrey')))
                        fig_scatter.update_layout(
                            height=500,
                            margin=dict(l=40, r=40, t=60, b=40)
                        )
                        st.plotly_chart(fig_scatter, use_container_width=True)
                    else:
                        st.info("No hay datos para mostrar la relación entre precio y ROI.")

                # Número medio de amenities por barrio
                st.markdown("#### Top 15 barrios por número medio de amenities")
                if 'amenities' in df_valencia.columns:
                    df_valencia['n_amenities'] = df_valencia['amenities'].str.count(',') + 1
                    barrio_amenities = df_valencia.groupby('neighbourhood')['n_amenities'].mean().reset_index()
                    barrio_amenities = barrio_amenities.sort_values(by='n_amenities', ascending=False).head(15)
                    if not barrio_amenities.empty:
                        fig_amenities = px.bar(
                            barrio_amenities,
                            x='n_amenities',
                            y='neighbourhood',
                            orientation='h',
                            labels={'n_amenities': 'Nº medio de amenities', 'neighbourhood': 'Barrio'},
                            title='Top 15 barrios por número medio de amenities',
                            color='n_amenities',
                            color_continuous_scale='Purples'
                        )
                        fig_amenities.update_layout(
                            height=500,
                            margin=dict(l=40, r=40, t=60, b=40),
                            yaxis=dict(tickfont=dict(size=12)),
                            xaxis=dict(tickfont=dict(size=12))
                        )
                        st.plotly_chart(fig_amenities, use_container_width=True)
                    else:
                        st.info("No hay datos de amenities para mostrar.")
                else:
                    st.info("No hay datos de amenities para mostrar.")

                # Número total de reseñas por barrio
                st.markdown("#### Top 15 barrios por número total de reseñas")
                if 'number_of_reviews' in df_valencia.columns:
                    barrio_mas_resenas = df_valencia.groupby('neighbourhood')['number_of_reviews'].sum().reset_index()
                    barrio_mas_resenas = barrio_mas_resenas.sort_values(by='number_of_reviews', ascending=False).head(15)
                    if not barrio_mas_resenas.empty:
                        fig_resenas = px.bar(
                            barrio_mas_resenas,
                            x='number_of_reviews',
                            y='neighbourhood',
                            orientation='h',
                            labels={'number_of_reviews': 'Número total de reseñas', 'neighbourhood': 'Barrio'},
                            title='Top 15 barrios por número total de reseñas',
                            color='number_of_reviews',
                            color_continuous_scale='Blues'
                        )
                        fig_resenas.update_layout(
                            height=500,
                            margin=dict(l=40, r=40, t=60, b=40),
                            yaxis=dict(tickfont=dict(size=12)),
                            xaxis=dict(tickfont=dict(size=12))
                        )
                        st.plotly_chart(fig_resenas, use_container_width=True)
                    else:
                        st.info("No hay datos de reseñas para mostrar.")
                else:
                    st.info("No hay datos de reseñas para mostrar.")

                # Habitaciones y baños por barrio
                st.markdown("#### Top 15 barrios por número medio de habitaciones y baños")
                if 'bedrooms' in df_valencia.columns and 'bathrooms' in df_valencia.columns:
                    barrio_habitaciones_banos = df_valencia.groupby('neighbourhood').agg({
                        'bedrooms': 'mean',
                        'bathrooms': 'mean'
                    }).reset_index()
                    barrio_habitaciones_banos = barrio_habitaciones_banos.sort_values(by='bedrooms', ascending=False).head(15)
                    if not barrio_habitaciones_banos.empty:
                        fig_hab = px.bar(
                            barrio_habitaciones_banos,
                            x='bedrooms',
                            y='neighbourhood',
                            orientation='h',
                            labels={'bedrooms': 'Habitaciones medias', 'neighbourhood': 'Barrio'},
                            title='Top 15 barrios por número medio de habitaciones',
                            color='bedrooms',
                            color_continuous_scale='Teal'
                        )
                        fig_hab.update_layout(
                            height=500,
                            margin=dict(l=40, r=40, t=60, b=40),
                            yaxis=dict(tickfont=dict(size=12)),
                            xaxis=dict(tickfont=dict(size=12))
                        )
                        st.plotly_chart(fig_hab, use_container_width=True)
                    else:
                        st.info("No hay datos de habitaciones para mostrar.")
                else:
                    st.info("No hay datos de habitaciones o baños para mostrar.")

                # Histograma de precios de alquiler
                st.markdown("#### Histograma de precios de alquiler")
                if 'price' in df_valencia.columns:
                    fig_hist = px.histogram(
                        df_valencia, x='price', nbins=40, color='neighbourhood',
                        labels={'price': 'Precio alquiler (€)'},
                        title='Distribución de precios de alquiler por barrio',
                        opacity=0.7
                    )
                    fig_hist.update_layout(
                        height=400,
                        margin=dict(l=40, r=40, t=60, b=40),
                        xaxis=dict(tickfont=dict(size=12)),
                        yaxis=dict(tickfont=dict(size=12)),
                        barmode='overlay'
                    )
                    st.plotly_chart(fig_hist, use_container_width=True)
                else:
                    st.info("No hay datos de precios para mostrar histograma.")

                # Boxplot de precios de alquiler por barrio (solo top 15 barrios)
                st.markdown("#### Boxplot de precios de alquiler por barrio (Top 15)")
                if 'price' in df_valencia.columns:
                    top_barrios = df_valencia['neighbourhood'].value_counts().head(15).index
                    df_top = df_valencia[df_valencia['neighbourhood'].isin(top_barrios)]
                    fig_box = px.box(
                        df_top, x='neighbourhood', y='price', points='outliers',
                        labels={'price': 'Precio alquiler (€)', 'neighbourhood': 'Barrio'},
                        title='Boxplot de precios de alquiler por barrio (Top 15)'
                    )
                    fig_box.update_layout(
                        height=500,
                        margin=dict(l=40, r=40, t=60, b=40),
                        xaxis=dict(tickangle=45, tickfont=dict(size=12)),
                        yaxis=dict(tickfont=dict(size=12))
                    )
                    st.plotly_chart(fig_box, use_container_width=True)
                else:
                    st.info("No hay datos de precios para mostrar boxplot.")

                # Histograma de ROI Neto
                st.markdown("#### Histograma de ROI Neto (%)")
                if 'Net ROI (%)' in df_valencia.columns:
                    fig_hist_roi = px.histogram(
                        df_valencia, x='Net ROI (%)', nbins=40, color='neighbourhood',
                        labels={'Net ROI (%)': 'ROI Neto (%)'},
                        title='Distribución de ROI Neto por barrio',
                        opacity=0.7
                    )
                    fig_hist_roi.update_layout(
                        height=400,
                        margin=dict(l=40, r=40, t=60, b=40),
                        xaxis=dict(tickfont=dict(size=12)),
                        yaxis=dict(tickfont=dict(size=12)),
                        barmode='overlay'
                    )
                    st.plotly_chart(fig_hist_roi, use_container_width=True)
                else:
                    st.info("No hay datos de ROI Neto para mostrar histograma.")

                # Boxplot de ROI Neto por barrio (solo top 15 barrios)
                st.markdown("#### Boxplot de ROI Neto por barrio (Top 15)")
                if 'Net ROI (%)' in df_valencia.columns:
                    top_barrios = df_valencia['neighbourhood'].value_counts().head(15).index
                    df_top = df_valencia[df_valencia['neighbourhood'].isin(top_barrios)]
                    fig_box_roi = px.box(
                        df_top, x='neighbourhood', y='Net ROI (%)', points='outliers',
                        labels={'Net ROI (%)': 'ROI Neto (%)', 'neighbourhood': 'Barrio'},
                        title='Boxplot de ROI Neto por barrio (Top 15)'
                    )
                    fig_box_roi.update_layout(
                        height=500,
                        margin=dict(l=40, r=40, t=60, b=40),
                        xaxis=dict(tickangle=45, tickfont=dict(size=12)),
                        yaxis=dict(tickfont=dict(size=12))
                    )
                    st.plotly_chart(fig_box_roi, use_container_width=True)
                else:
                    st.info("No hay datos de ROI Neto para mostrar boxplot.")

                # Histograma de días alquilados
                st.markdown("#### Histograma de días alquilados")
                if 'days_rented' in df_valencia.columns:
                    fig_hist_days = px.histogram(
                        df_valencia, x='days_rented', nbins=40, color='neighbourhood',
                        labels={'days_rented': 'Días alquilados'},
                        title='Distribución de días alquilados por barrio',
                        opacity=0.7
                    )
                    fig_hist_days.update_layout(
                        height=400,
                        margin=dict(l=40, r=40, t=60, b=40),
                        xaxis=dict(tickfont=dict(size=12)),
                        yaxis=dict(tickfont=dict(size=12)),
                        barmode='overlay'
                    )
                    st.plotly_chart(fig_hist_days, use_container_width=True)
                else:
                    st.info("No hay datos de días alquilados para mostrar histograma.")

                # Boxplot de días alquilados por barrio (solo top 15 barrios)
                st.markdown("#### Boxplot de días alquilados por barrio (Top 15)")
                if 'days_rented' in df_valencia.columns:
                    top_barrios = df_valencia['neighbourhood'].value_counts().head(15).index
                    df_top = df_valencia[df_valencia['neighbourhood'].isin(top_barrios)]
                    fig_box_days = px.box(
                        df_top, x='neighbourhood', y='days_rented', points='outliers',
                        labels={'days_rented': 'Días alquilados', 'neighbourhood': 'Barrio'},
                        title='Boxplot de días alquilados por barrio (Top 15)'
                    )
                    fig_box_days.update_layout(
                        height=500,
                        margin=dict(l=40, r=40, t=60, b=40),
                        xaxis=dict(tickangle=45, tickfont=dict(size=12)),
                        yaxis=dict(tickfont=dict(size=12))
                    )
                    st.plotly_chart(fig_box_days, use_container_width=True)
                else:
                    st.info("No hay datos de días alquilados para mostrar boxplot.")

                # Mapa de puntos de los anuncios (si hay lat/lon)
                st.markdown("#### Mapa de anuncios")
                if 'latitude' in df_valencia.columns and 'longitude' in df_valencia.columns:
                    st.map(df_valencia[['latitude', 'longitude']].dropna())
                else:
                    st.info("No hay datos de localización para mostrar el mapa.")

                # Delincuencia: Gráfico de barras agrupadas y heatmap
                st.markdown("#### Delitos denunciados en Valencia por año")
                if df_delincuencia is not None and not df_delincuencia.empty:
                    df_delincuencia_filtrado = df_delincuencia[df_delincuencia['Parámetro'] != 'Total']
                    fig, ax = plt.subplots(figsize=(14, 7))
                    sns.barplot(
                        data=df_delincuencia_filtrado,
                        x='Año',
                        y='Denuncias',
                        hue='Parámetro',
                        ax=ax
                    )
                    ax.set_title('Delitos denunciados en Valencia por año')
                    ax.set_ylabel('Número de denuncias')
                    ax.set_xlabel('Año')
                    ax.legend(title='Tipo de delito', bbox_to_anchor=(1.05, 1), loc='upper left')
                    plt.tight_layout()
                    st.pyplot(fig)

                    st.markdown("#### Mapa de calor de delitos denunciados en Valencia por tipo y año")
                    fig2, ax2 = plt.subplots(figsize=(14, 7))
                    heatmap_data = df_delincuencia_filtrado.pivot_table(
                        index='Parámetro',
                        columns='Año',
                        values='Denuncias',
                        aggfunc='sum'
                    ).fillna(0)
                    sns.heatmap(
                        heatmap_data,
                        cmap='YlOrRd',
                        annot=True,
                        fmt='.0f',
                        linewidths=.5,
                        cbar_kws={'label': 'Número de denuncias'},
                        annot_kws={"size": 10},
                        ax=ax2
                    )
                    ax2.set_title('Mapa de calor de delitos denunciados en Valencia por tipo y año')
                    ax2.set_xlabel('Año')
                    ax2.set_ylabel('Tipo de delito')
                    plt.xticks(rotation=45)
                    plt.tight_layout()
                    st.pyplot(fig2)
                else:
                    st.info("No hay datos de delincuencia para mostrar.")
            else:
                st.info("No hay datos para mostrar en esta pestaña.")

        elif ciudad_actual.lower() == "barcelona":
                st.info("Si la ciudad es barcelona añadir codigo aqui")
        elif ciudad_actual.lower() == "malaga":
                st.info("Si la ciudad es malaga añadir codigo aqui")
        elif ciudad_actual.lower() == "madrid":
                st.subheader("🔍 Análisis Avanzado para Madrid")
            
            # Relación entre precio medio de alquiler y rentabilidad estimada
            st.markdown("#### Relación entre precio medio de alquiler y rentabilidad estimada por barrio")
            if 'price' in df_ciudad.columns and 'estimated_revenue_l365d' in df_ciudad.columns:
                fig_scatter = px.scatter(
                    df_ciudad,
                    x='price',
                    y='estimated_revenue_l365d',
                    color='neighbourhood',
                    hover_data=['neighbourhood'],
                    labels={'price': 'Precio alquiler (€)', 'estimated_revenue_l365d': 'Rentabilidad Estimada (€)', 'neighbourhood': 'Barrio'},
                    title='Relación entre precio de alquiler y rentabilidad estimada por barrio (Madrid)'
                )
                st.plotly_chart(fig_scatter, use_container_width=True)
            else:
                st.info("No hay datos suficientes para mostrar el gráfico de dispersión.")

            # Rentabilidad media por número de habitaciones
            st.markdown("#### Rentabilidad media por número de habitaciones")
            if 'bedrooms' in df_ciudad.columns and 'estimated_revenue_l365d' in df_ciudad.columns:
                rentabilidad_habitaciones = df_ciudad.groupby('bedrooms')['estimated_revenue_l365d'].mean().reset_index()
                fig_habitaciones = px.bar(
                    rentabilidad_habitaciones,
                    x='bedrooms',
                    y='estimated_revenue_l365d',
                    labels={'bedrooms': 'Número de habitaciones', 'estimated_revenue_l365d': 'Rentabilidad Estimada (€)'},
                    title='Rentabilidad media por número de habitaciones'
                )
                st.plotly_chart(fig_habitaciones, use_container_width=True)
            else:
                st.info("No hay datos suficientes para mostrar la rentabilidad por número de habitaciones.")

            # Rentabilidad media por número de baños
            st.markdown("#### Rentabilidad media por número de baños")
            if 'bathrooms' in df_ciudad.columns and 'estimated_revenue_l365d' in df_ciudad.columns:
                rentabilidad_banos = df_ciudad.groupby('bathrooms')['estimated_revenue_l365d'].mean().reset_index()
                fig_banos = px.bar(
                    rentabilidad_banos,
                    x='bathrooms',
                    y='estimated_revenue_l365d',
                    labels={'bathrooms': 'Número de baños', 'estimated_revenue_l365d': 'Rentabilidad Estimada (€)'},
                    title='Rentabilidad media por número de baños'
                )
                st.plotly_chart(fig_banos, use_container_width=True)
            else:
                st.info("No hay datos suficientes para mostrar la rentabilidad por número de baños.")
        else:
            st.info("No hay datos para mostrar en esta pestaña.")

# ------------------ Pestaña 6: Conclusiones ------------------
if len(main_tabs) > 5:
    with main_tabs[5]:
        if ciudad_actual.lower() == "valencia":
            st.subheader("Conclusiones finales para empresas interesadas en invertir en alquiler turístico en Valencia (AirBnB)")
            st.markdown("""
            El análisis exhaustivo de los datos de rentabilidad, competencia, demanda, precios y características de los barrios de Valencia permite extraer recomendaciones más precisas y accionables para empresas que buscan invertir en el mercado de alquiler turístico:

            **Rentabilidad y retorno de inversión:** Los barrios líderes en rentabilidad neta y bruta, como Ciutat Universitaria, Cami Fondo, Penya-Roja y La Roqueta, ofrecen retornos superiores al promedio de la ciudad. Sin embargo, la diferencia entre rentabilidad bruta y neta es relativamente baja en los barrios más rentables, lo que indica una estructura de costes eficiente y un mercado consolidado.

            **Demanda sostenida y visibilidad:** Barrios como Cabanyal-Canyamelar, Russafa y El Mercat destacan por su alto volumen de reseñas totales y mensuales, reflejando una demanda turística constante y una elevada rotación de huéspedes. Invertir en estas zonas garantiza visibilidad y ocupación, aunque implica enfrentarse a una competencia intensa.

            **Competencia y saturación:** La saturación de anuncios es especialmente alta en barrios turísticos y céntricos. Para destacar en estos mercados, es fundamental apostar por la diferenciación, la calidad del alojamiento y la experiencia del huésped. Por otro lado, existen barrios con alta rentabilidad y baja competencia (menor número de anuncios), que representan oportunidades para captar reservas con menor riesgo de saturación.

            **Calidad, amenities y tamaño de la vivienda:** Los barrios con mayor número medio de amenities y viviendas más espaciosas tienden a lograr mejores valoraciones y mayor rentabilidad. La inversión en equipamiento y servicios adicionales puede ser clave para maximizar ingresos y diferenciarse en mercados competitivos.

            **Diversidad de precios y accesibilidad:** Valencia presenta una amplia dispersión de precios de alquiler y compra por metro cuadrado, tanto entre barrios como dentro de cada uno. Esto permite adaptar la estrategia de inversión según el presupuesto y el perfil de riesgo, desde zonas premium hasta barrios emergentes con potencial de revalorización.

            **Relación entre precio y competencia:** Los barrios con precios de alquiler más altos suelen concentrar también mayor competencia. Sin embargo, existen zonas con precios elevados y menor saturación, que pueden ser especialmente atractivas para inversores que buscan maximizar ingresos sin enfrentarse a una oferta excesiva.

            **Factores adicionales:** Es imprescindible monitorizar la evolución de la normativa local, la estacionalidad de la demanda, la seguridad y otros factores externos que pueden impactar la rentabilidad y la sostenibilidad de la inversión.

            **Recomendación estratégica:**  
            La mejor estrategia combina la selección de barrios con alta rentabilidad neta, demanda sostenida y competencia controlada, junto con una apuesta por la calidad, el equipamiento y la diferenciación. Diversificar la cartera en diferentes zonas y perfiles de barrio permite equilibrar riesgo y retorno. Además, es clave realizar un seguimiento continuo de los indicadores clave del mercado y adaptar la oferta a las tendencias y preferencias de los huéspedes.

            En resumen, Valencia ofrece un mercado dinámico y diverso, con grandes oportunidades para empresas de alquiler turístico. El éxito dependerá de una toma de decisiones basada en datos, una gestión activa y una visión integral que combine rentabilidad, demanda, competencia y calidad.
                """)
        elif ciudad_actual.lower() == "barcelona":
            st.info("Si la ciudad es barcelona añadir codigo aqui")

        elif ciudad_actual.lower() == "malaga":
            st.info("Si la ciudad es barcelona añadir codigo aqui")

        elif ciudad_actual.lower() == "madrid":
            st.subheader("📝 Conclusiones finales para empresas interesadas en invertir en alquiler turístico en Madrid")
            st.markdown("""
            Madrid ofrece un mercado inmobiliario dinámico y diverso, con oportunidades significativas para empresas interesadas en el alquiler turístico. 
            Los barrios céntricos destacan por su alta rentabilidad y demanda sostenida, mientras que las zonas periféricas ofrecen opciones más accesibles con menor competencia.

            **Recomendaciones clave:**
            - Priorizar barrios con alta rentabilidad y demanda sostenida.
            - Invertir en propiedades con características diferenciadoras y amenities.
            - Monitorizar la evolución de la normativa local y las tendencias del mercado.

            En resumen, Madrid es una ciudad con un mercado inmobiliario atractivo para el alquiler turístico, pero requiere una estrategia basada en datos y adaptada a las condiciones locales.
            """)
        else:
            st.info("No hay datos para mostrar en esta pestaña.")

# ------------------ Descargable ------------------
with st.expander("Ver datos en formato tabla"):
    if not df_valencia.empty:
        st.dataframe(df_valencia, use_container_width=True)
        csv = df_valencia.to_csv(index=False).encode('utf-8')
        st.download_button(
            "Descargar datos filtrados (CSV)",
            data=csv,
            file_name="valencia_inmobiliario.csv",
            mime="text/csv",
        )
    else:
        st.info("No hay datos para mostrar o descargar.")

# ------------ Información del dashboard ------------
st.sidebar.markdown("---")
st.sidebar.info("""
**Acerca de este Panel**

Este panel muestra datos del mercado inmobiliario de Valencia, Málaga, Madrid y Barcelona para análisis de inversión.
Desarrollado con Streamlit, Plotly Express y Seaborn.
""")

