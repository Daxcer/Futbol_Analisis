import streamlit as st
import pandas as pd
import plotly.express as px  # Para gráficos interactivos
import os

# Cargar los datos
data = pd.read_csv('datos/data.csv')

# Título de la página
st.title("Análisis por Equipo")

# Descripción de la funcionalidad
st.write("""
    Selecciona un equipo de la Premier League y una temporada para explorar su rendimiento.
    Además, puedes comparar el rendimiento del equipo a lo largo de las diferentes temporadas disponibles.
""")

# ListBox para seleccionar el equipo (ordenado alfabéticamente)
equipo_seleccionado = st.selectbox("Selecciona un equipo", sorted(data['Squad'].unique()))

# ListBox para seleccionar la temporada
temporada_seleccionada = st.selectbox("Selecciona una temporada", data['Season'].unique())

# Cargar una imagen del equipo seleccionado (puedes tener una carpeta con las imágenes)
# Asumimos que las imágenes están nombradas como "equipo.png" en la carpeta 'imagenes/'
ruta_imagen = f'imagenes/{equipo_seleccionado}.png'
st.image(ruta_imagen, caption=f"Imagen del equipo {equipo_seleccionado}", use_column_width=True)

# Filtrar los datos para el equipo y la temporada seleccionados
filtro = (data['Squad'] == equipo_seleccionado) & (data['Season'] == temporada_seleccionada)
datos_equipo = data[filtro]

# Mostrar algunos datos relevantes
st.subheader(f"Datos relevantes de {equipo_seleccionado} en la temporada {temporada_seleccionada}")
st.write(f"Goles a favor: {datos_equipo['GF'].values[0]}")
st.write(f"Goles en contra: {datos_equipo['GA'].values[0]}")
st.write(f"Puntos obtenidos: {datos_equipo['Pts'].values[0]}")
st.write(f"Tiros al arco: {datos_equipo['Performance_SoTA'].values[0]}")
st.write(f"Expected Goals (xG): {datos_equipo['Expected_xG'].values[0]}")

# Seleccionar variables a comparar en el gráfico
st.subheader("Comparativa de variables a lo largo de las temporadas")

# ListBox para seleccionar la variable a comparar
variable_comparar = st.selectbox("Selecciona una variable para comparar", ['GF', 'GA', 'Pts', 'SoT', 'Expected_xG'])

# Filtrar los datos de ese equipo en todas las temporadas
datos_comparacion = data[data['Squad'] == equipo_seleccionado].sort_values(by='Season', ascending=False)

# Crear gráfico interactivo con Plotly
fig = px.line(datos_comparacion, x='Season', y=variable_comparar, 
              title=f"Comparativa de {variable_comparar} para {equipo_seleccionado} a lo largo de las temporadas",
              markers=True)

# Invertir el orden del eje X para mostrar las temporadas más recientes primero
fig.update_layout(xaxis=dict(autorange="reversed"))

# Mostrar el gráfico
st.plotly_chart(fig)

