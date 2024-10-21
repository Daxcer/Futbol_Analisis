import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
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
equipo_seleccionado = st.selectbox("Selecciona un equipo", sorted(data['Squad'].unique()), key="equipo_selectbox")

# ListBox para seleccionar la temporada
temporada_seleccionada = st.selectbox("Selecciona una temporada", data['Season'].unique(), key="temporada_selectbox")

# Cargar una imagen del equipo seleccionado
# Las imágenes están nombradas como "equipo.png" en la carpeta 'imagenes/'
ruta_imagen = f'imagenes/{equipo_seleccionado}.png'
st.image(ruta_imagen, caption=f"Imagen del equipo {equipo_seleccionado}", use_column_width=True)

# Filtrar los datos para el equipo y la temporada seleccionados
filtro = (data['Squad'] == equipo_seleccionado) & (data['Season'] == temporada_seleccionada)
datos_equipo = data[filtro]

# Obtener el ranking
ranking = datos_equipo['Rk'].values[0]

# Mostrar el ranking centrado
st.markdown(f"<h3 style='text-align: center;'>Ranking:  {ranking}°</h3>", unsafe_allow_html=True)

# Selectbox para seleccionar el tipo de análisis
tipo_analisis = st.selectbox("Selecciona el tipo de análisis", ["Ataque", "Defensa", "Pases", "Posesión"])

# Definir las columnas asociadas a cada tipo de análisis
analisis_columnas = {
    "Ataque": ['GF', 'Expected_xG', 'Performance_Ast', 'Expected_xA', 'Standard_Sh', 'Standard_SoT', 'Standard_Dist', 'SCA_SCA', 'GCA_GCA'],
    "Defensa": ['Tackles_Tkl', 'Tackles_TklW', 'Tackles_Def3rd', 'Tackles_Mid3rd', 'Tackles_Att3rd', 'Blocks_Blocks', 'Blocks_Int', 'Blocks_Clr', 'Blocks_Err'],
    "Pases": ['Total_PasCmp', 'Total_PasAtt', 'Total_TotDist', 'Total_PrgDist', 'Expected_KP', 'Expected_F1/3', 'Expected_PPA', 'Expected_CrsPA', 'Expected_PrgP'],
    "Posesión": ['Touches_Touches', 'Poss', 'Take-Ons_Att', 'Take-Ons_Succ', 'Receiving_Rec', 'Receiving_PrgR', 'Carries_Carries', 'Carries_PrgC', 'Carries_Mis']
}

# Definimos un alias para cada columna
alias_columnas = {
    'GF': 'GF',
    'Expected_xG': 'xG',
    'Performance_Ast': 'Ast',
    'Expected_xA': 'xA',
    'Standard_Sh': 'Sh',
    'Standard_SoT': 'SoT',
    'Standard_Dist': 'ShDist',
    'SCA_SCA': 'SCA',
    'GCA_GCA': 'GCA',
    'Tackles_Tkl': 'Tkl',
    'Tackles_TklW': 'TklW',
    'Tackles_Def3rd': 'Tkl3/3',
    'Tackles_Mid3rd': 'Tkl2/3',
    'Tackles_Att3rd': 'Tkl1/3',
    'Blocks_Blocks': 'Blocks',
    'Blocks_Int': 'Int',
    'Blocks_Clr': 'Clr',
    'Blocks_Err': 'Err',
    'Total_PasCmp': 'PasCmp',
    'Total_PasAtt': 'PasAtt',
    'Total_TotDist': 'TotDist',
    'Total_PrgDist': 'PrgDist',
    'Expected_KP': 'KP',
    'Expected_F1/3': 'Pas1/3',
    'Expected_PPA': 'PasPA',
    'Expected_CrsPA': 'CrsPA',
    'Expected_PrgP': 'PrgP',
    'Touches_Touches': 'Touches',
    'Poss': 'Poss',
    'Take-Ons_Att': 'TkOAtt',
    'Take-Ons_Succ': 'TkOSucc',
    'Receiving_Rec': 'PossRec',
    'Receiving_PrgR': 'PrgR',
    'Carries_Carries': 'Carries',
    'Carries_PrgC': 'PrgC',
    'Carries_Mis': 'Mis'
}

# Mostrar los datos relevantes para el tipo de análisis seleccionado
def mostrar_analisis_tabla(tipo_analisis):
    st.subheader(f"Datos relevantes de {equipo_seleccionado} en la temporada {temporada_seleccionada} ({tipo_analisis})")

    columnas = analisis_columnas[tipo_analisis]
    
    # Crear tres columnas
    col1, col2, col3 = st.columns(3)

    # Iterar sobre las columnas y asignar los valores a cada columna
    for i, columna in enumerate(columnas):
        if i < 3:
            col1.metric(alias_columnas[columna], datos_equipo[columna].values[0])
        elif 3 <= i < 6:
            col2.metric(alias_columnas[columna], datos_equipo[columna].values[0])
        else:
            col3.metric(alias_columnas[columna], datos_equipo[columna].values[0])

# Llamar a la función con el tipo de análisis seleccionado
mostrar_analisis_tabla(tipo_analisis)

# Filtrar los datos de ese equipo en todas las temporadas
datos_comparacion = data[data['Squad'] == equipo_seleccionado].sort_values(by='Season', ascending=False)

# Gráfico de dispersión para comparar dos variables
st.subheader("Gráfico de Dispersión: Comparación entre dos variables")
variable_x = st.selectbox("Selecciona la variable para el eje X", [alias_columnas[col] for col in analisis_columnas[tipo_analisis]])
variable_y = st.selectbox("Selecciona la variable para el eje Y", [alias_columnas[col] for col in analisis_columnas[tipo_analisis]])

# Mapeamos los alias al nombre de las columnas originales
variable_x_orig = [col for col, alias in alias_columnas.items() if alias == variable_x][0]
variable_y_orig = [col for col, alias in alias_columnas.items() if alias == variable_y][0]

fig = px.scatter(datos_comparacion, x=variable_x_orig, y=variable_y_orig,
                 title=f"Dispersión de {variable_x} vs {variable_y} ({equipo_seleccionado})",
                 labels={variable_x_orig: variable_x, variable_y_orig: variable_y},
                 hover_data=['Season'])  # Agregamos las temporadas al hover
st.plotly_chart(fig)

# Gráfico de línea para una variable a lo largo de las temporadas
st.subheader("Gráfico de Línea: Comparación a lo largo de las temporadas")
variable_comparar = st.selectbox("Selecciona una variable para comparar", [alias_columnas[col] for col in analisis_columnas[tipo_analisis]], key='variable_linea')

# Mapeamos el alias al nombre de la columna original
variable_comparar_orig = [col for col, alias in alias_columnas.items() if alias == variable_comparar][0]

fig = px.line(datos_comparacion, x='Season', y=variable_comparar_orig, 
              title=f"Comparativa de {variable_comparar} para {equipo_seleccionado} a lo largo de las temporadas",
              markers=True)

fig.update_layout(xaxis=dict(autorange="reversed"))
st.plotly_chart(fig)

# Gráfico de barras simple para una variable
st.subheader("Gráfico de Barras: Comparación de una variable a lo largo de las temporadas")

# Selectbox para elegir la variable
variable_comparar = st.selectbox("Selecciona una variable para comparar", [alias_columnas[col] for col in analisis_columnas[tipo_analisis]], key='variable_barra')

# Mapeamos el alias al nombre de la columna original
variable_comparar_orig = [col for col, alias in alias_columnas.items() if alias == variable_comparar][0]

# Creamos el gráfico
fig = go.Figure(data=go.Bar(
    x=datos_comparacion['Season'],
    y=datos_comparacion[variable_comparar_orig],
    name=variable_comparar
))

fig.update_layout(
    title=f"Comparativa de {variable_comparar} para {equipo_seleccionado} a lo largo de las temporadas",
    xaxis_title="Temporada",
    yaxis_title="Valor",
    xaxis=dict(autorange="reversed")
)

fig.update_traces(marker_color='blue', opacity=0.7)

st.plotly_chart(fig)