import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import sqlite3


# Función para conectar a la base de datos
def connect_db(db_name):
    return sqlite3.connect(db_name)

# Función para listar equipos por temporada
def list_teams_by_season(conn, season):
    query = f'SELECT DISTINCT "Squad" FROM "{season}_stats_standard";'
    teams = pd.read_sql_query(query, conn)
    return teams['Squad'].tolist()

# Función para obtener las estadísticas de un equipo y una tabla
def get_team_stats(conn, season, table, team, selected_columns=None):
    query = f'SELECT * FROM "{season}_{table}" WHERE "Squad" = "{team}";'
    df = pd.read_sql_query(query, conn)
    if selected_columns:
        df = df[selected_columns]
    return df

# Función para seleccionar solo las columnas necesarias
def filter_columns(df, selected_columns):
    df = df.apply(pd.to_numeric, errors='ignore')
    return df[selected_columns]

# Función para crear el Pizza Chart de un jugador
def get_players_stats(conn, season, team):
    columns = ['Player', 'Pos', 'standard_MP', 'standard_Min', 
               'standard_Gls', 'standard_Ast', 'shooting_Sh', 'shooting_SoT', 
               'passing_Cmp%', 'defense_TklW', 'defense_Int', 
               'misc_Fls', 'misc_Fld', 'misc_CrdY', 'misc_CrdR']
    
    standard_stats = get_team_stats(conn, season, 'stats_standard', team, ['Player', 'Pos', 'standard_MP', 'standard_Min', 'standard_Gls', 'standard_Ast'])
    shooting_stats = get_team_stats(conn, season, 'stats_shooting', team, ['Player', 'shooting_Sh', 'shooting_SoT'])
    passing_stats = get_team_stats(conn, season, 'stats_passing', team, ['Player', 'passing_Cmp%'])
    defense_stats = get_team_stats(conn, season, 'stats_defense', team, ['Player', 'defense_TklW', 'defense_Int'])
    misc_stats = get_team_stats(conn, season, 'stats_misc', team, ['Player', 'misc_Fls', 'misc_Fld', 'misc_CrdY', 'misc_CrdR'])
    
    combined_df = pd.merge(standard_stats, shooting_stats, on='Player')
    combined_df = pd.merge(combined_df, passing_stats, on='Player')
    combined_df = pd.merge(combined_df, defense_stats, on='Player')
    combined_df = pd.merge(combined_df, misc_stats, on='Player')
    
    return filter_columns(combined_df, columns)

# Función para obtener las estadísticas combinadas de un jugador
def get_combined_stats(conn, season, team):
    # Obtener datos de cada tabla relevante
    shooting_stats = get_team_stats(conn, season, 'stats_shooting', team, ['Player', 'shooting_SoT/90', 'shooting_Sh'])
    gca_stats = get_team_stats(conn, season, 'stats_gca', team, ['Player', 'gca_SCA90'])
    possession_stats = get_team_stats(conn, season, 'stats_possession', team, ['Player', 'possession_Att Pen', 'possession_Succ', 'possession_Rec'])
    passing_stats = get_team_stats(conn, season, 'stats_passing', team, ['Player', 'passing_Att', 'passing_Cmp', 'passing_KP', 'passing_PrgP'])
    misc_stats = get_team_stats(conn, season, 'stats_misc', team, ['Player', 'misc_TklW', 'misc_Int', 'misc_Recov', 'misc_Fls', 'misc_Won'])
    standard_stats = get_team_stats(conn, season, 'stats_standard', team, ['Player', 'Pos', 'standard_MP', 'standard_Min'])

    # Fusionar los DataFrames por la columna 'Player'
    combined_df = pd.merge(shooting_stats, gca_stats, on='Player', how='inner')
    combined_df = pd.merge(combined_df, possession_stats, on='Player', how='inner')
    combined_df = pd.merge(combined_df, passing_stats, on='Player', how='inner')
    combined_df = pd.merge(combined_df, misc_stats, on='Player', how='inner')
    combined_df = pd.merge(combined_df, standard_stats, on='Player', how='inner')

    return combined_df


# Función para obtener y calcular los percentiles de toda la liga
def get_percentile_data(conn, season, team):
    # Obtener datos de cada tabla relevante para toda la liga
    shooting_stats = get_team_stats(conn, season, 'stats_shooting', team, ['Player', 'Squad', 'shooting_SoT/90', 'shooting_Sh'])
    gca_stats = get_team_stats(conn, season, 'stats_gca', team, ['Player', 'Squad', 'gca_SCA90'])
    possession_stats = get_team_stats(conn, season, 'stats_possession', team, ['Player', 'Squad', 'possession_Att Pen', 'possession_Succ', 'possession_Rec'])
    passing_stats = get_team_stats(conn, season, 'stats_passing', team, ['Player', 'Squad', 'passing_Att', 'passing_Cmp', 'passing_KP', 'passing_PrgP'])
    misc_stats = get_team_stats(conn, season, 'stats_misc', team, ['Player', 'Squad', 'misc_TklW', 'misc_Int', 'misc_Recov', 'misc_Fls', 'misc_Won'])
    standard_stats = get_team_stats(conn, season, 'stats_standard', team, ['Player', 'Squad', 'Pos', 'standard_MP', 'standard_Min'])

    # Fusionar los DataFrames por la columna 'Player' para obtener los datos completos de la liga
    combined_df = pd.merge(shooting_stats, gca_stats, on=['Player', 'Squad'], how='inner')
    combined_df = pd.merge(combined_df, possession_stats, on=['Player', 'Squad'], how='inner')
    combined_df = pd.merge(combined_df, passing_stats, on=['Player', 'Squad'], how='inner')
    combined_df = pd.merge(combined_df, misc_stats, on=['Player', 'Squad'], how='inner')
    combined_df = pd.merge(combined_df, standard_stats, on=['Player', 'Squad'], how='inner')

    # Filtrar los datos del equipo actual si es necesario
    combined_df_team = combined_df[combined_df['Squad'] == team]

    return combined_df_team

# Función para calcular percentiles filtrando por posición y minutos jugados
def calculate_percentiles(df, columns, season, min_minutes_pct=0.25):
    # Limpiar las posiciones y usar solo la posición primaria
    df['Pos'] = clean_position(df['Pos'])

    # Calcular el total de partidos jugados en la temporada actual
    df['standard_MP'] = pd.to_numeric(df['standard_MP'], errors='coerce')
    total_matches_played = df['standard_MP'].max()

    # Calcular los minutos máximos en la temporada actual
    max_minutes = get_max_minutes(season, total_matches_played)

    # Filtrar jugadores que hayan jugado al menos un % de los minutos
    df['standard_Min'] = pd.to_numeric(df['standard_Min'], errors='coerce')
    df = df[df['standard_Min'] >= min_minutes_pct * max_minutes]

    # Calcular percentiles por posición (comparamos solo jugadores con la misma posición primaria)
    for pos in df['Pos'].unique():
        df_pos = df[df['Pos'] == pos]
        for col in columns:
            df.loc[df['Pos'] == pos, f'Percentil_{col}'] = df_pos[col].rank(pct=True) * 100

    return df

# Función para procesar la columna de posición y obtener solo la posición primaria
def clean_position(pos_column):
    # Extraer la primera posición antes de la coma si hay varias posiciones
    return pos_column.str.split(',').str[0].str.strip()

# Función para calcular los minutos máximos jugados en una temporada
def get_max_minutes(season, total_matches_played):
    # Temporadas estándar (38 partidos)
    if season != '2024-2025':
        return 38 * 90
    # Temporada actual (basada en los partidos jugados hasta ahora)
    else:
        return total_matches_played * 90

# Función para cambiar los nombres de las columnas de percentiles
def rename_columns(column_names, rename_dict):
    return [rename_dict.get(col, col) for col in column_names]

# Función para crear un gráfico de "pizza" con fondo negro y colores vivos
def pizza_chart(data, player_name, season_selected, team_selected, pos, rename_dict=None):
    # Dividir las métricas en tres categorías
    attacking = ['Percentil_shooting_Sh', 'Percentil_shooting_SoT/90', 'Percentil_gca_SCA90', 'Percentil_possession_Att Pen', 'Percentil_possession_Succ']
    possession = ['Percentil_passing_Att', 'Percentil_passing_Cmp', 'Percentil_passing_KP', 'Percentil_passing_PrgP', 'Percentil_possession_Rec']
    defending = ['Percentil_misc_TklW', 'Percentil_misc_Int', 'Percentil_misc_Recov', 'Percentil_misc_Fls', 'Percentil_misc_Won']

    metrics = attacking + possession + defending
    values = data[data['Player'] == player_name][metrics].values.flatten().tolist()

    # Normalizar los valores para el gráfico de pizza
    values += values[:1]  # Repetimos el primero para cerrar el círculo

    # Crear los ángulos para el gráfico
    num_vars = len(metrics)
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
    angles += angles[:1]

    # Si se proporcionó un diccionario de renombres, actualizar las etiquetas
    if rename_dict:
        metrics = rename_columns(metrics, rename_dict)

    # Configurar el gráfico de pizza
    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(polar=True))  # Tamaño ajustado del gráfico
    fig.patch.set_facecolor('black')  # Fondo negro
    ax.set_facecolor('black')  # Fondo negro en el gráfico

    # Dibujar segmentos individuales para cada métrica
    for i, (angle, value) in enumerate(zip(angles[:-1], values[:-1])):
        # Determinar el color según la categoría
        if i < len(attacking):
            color = '#EC313A'  # Rojo vivo para ataque
        elif i < len(attacking) + len(possession):
            color = '#1CD787'  # Verde vivo para posesión
        else:
            color = '#0E70BE'  # Azul vivo para defensa
        
        # Dibujar un segmento de "pizza" para cada métrica
        ax.bar(angle, value, width=2*np.pi/num_vars, color=color, edgecolor='white', alpha=1.0, align='edge')

        # Colocar los valores en el borde superior de la rebanada, centrado
        # Mover ligeramente la posición angular para que esté entre las divisiones
        angle_middle = angle + (np.pi / num_vars)  # Centro entre dos ángulos
        bbox_props = dict(boxstyle="round,pad=0.3", facecolor=color, edgecolor="white", linewidth=2)
        ax.text(angle_middle, value, f'{value:.0f}', horizontalalignment='center', verticalalignment='center', size=10, color='white', weight='semibold', bbox=bbox_props)

    # Ajustar el radio del círculo del gráfico para que el centro sea más pequeño
    ax.set_ylim(0, 120)  # Hacemos que el círculo central sea más pequeño al extender el eje y
    
    # Añadir etiquetas a cada métrica en el centro de la rebanada
    ax.set_yticklabels([])  # Quitamos los labels de las líneas circulares
    ax.set_xticks(angles[:-1])  # Los ángulos para las etiquetas
    ax.set_xticklabels(metrics, fontsize=12, fontweight='bold', color='white', wrap=True)  # Nombres en blanco y en negritas
    for label, angle in zip(ax.get_xticklabels(), angles[:-1]):
        label.set_horizontalalignment('center')  # Centrar el texto entre las rebanadas

    # Ajustar el límite del gráfico para que las líneas divisorias no se superpongan
    ax.set_ylim(0, 105)  # Esto mantiene los valores dentro del rango de 0 a 100

    # Añadir título personalizado
    plt.title(f'{player_name}, {season_selected}', size=20, color='white', pad=20)  # Título principal
    plt.text(0, -1.2, f'{team_selected}, {pos}', ha='center', size=15, color='white')  # Subtítulo debajo del título

    # Añadir glosario de colores debajo del gráfico
    plt.text(-0.7, -1.6, 'Rojo - Ataque', ha='center', size=12, color='#EC313A', bbox=dict(facecolor='black', edgecolor='none'))
    plt.text(0, -1.6, 'Verde - Posesión', ha='center', size=12, color='#1CD787', bbox=dict(facecolor='black', edgecolor='none'))
    plt.text(0.7, -1.6, 'Azul - Defensa', ha='center', size=12, color='#0E70BE', bbox=dict(facecolor='black', edgecolor='none'))

    # Añadir la descripción de los percentiles
    plt.text(0, -2.0, '* valores convertidos a percentiles en la Premier League', ha='center', size=10, color='white', style='italic')

    return fig


# Configuración de Streamlit
st.title("Análisis Avanzado de Desempeño de Jugadores")

# Descripción de la funcionalidad
st.write("""
    Explora detalladamente las estadísticas de los jugadores de fútbol a lo largo de las temporadas seleccionadas. Con esta herramienta podrás:

**Seleccionar una Temporada y Equipo:** Navega a través de varias temporadas para obtener un contexto detallado y actual de cada equipo.

**Visualizar el Desempeño de Jugadores en Formato de Pizza Chart:** El gráfico de pizza, segmentado en categorías de ataque, posesión y defensa, te permitirá comparar el rendimiento del jugador seleccionado en diferentes aspectos del juego. Los valores de las métricas están convertidos a percentiles de la liga, proporcionando una referencia visual clara sobre cómo se posiciona el jugador en comparación con sus colegas.

**Ver Estadísticas en Detalle:** Los datos de cada jugador se muestran en una tabla para una referencia numérica exacta. Aquí puedes explorar sus goles, asistencias, intercepciones, pases, entre otras estadísticas clave.
""")

# Conectar a la base de datos
conn = connect_db('C:/Users/danag.LAPTOP-A0ADBJQ7/Downloads/Clases_Diplomado/proyecto_final/datos/model_data.db')

# Crear columnas para la alineación
col1, col2 = st.columns([2, 1])

# Selectbox para la temporada (en col1)
with col1:
    seasons = ['2024-2025', '2023-2024', '2022-2023', '2021-2022', '2020-2021', '2019-2020', '2018-2019']
    season_selected = st.selectbox("Selecciona la temporada", seasons)

    # Obtener equipos de la temporada seleccionada
    teams = sorted(list_teams_by_season(conn, season_selected))
    team_selected = st.selectbox("Selecciona el equipo", teams)

# Mostrar imagen en col2
with col2:
    image_path = f'./imagenes/{team_selected}.png'
    if os.path.exists(image_path):
        st.image(image_path, caption=team_selected, use_column_width=True)
    else:
        st.write(f"No se encontró la imagen del equipo {team_selected}")

# Mostrar las estadísticas de jugadores
st.write(f"Estadísticas de jugadores del equipo **{team_selected}** en la temporada {season_selected}")
players_df = get_players_stats(conn, season_selected, team_selected)
st.dataframe(players_df)

# Obtener estadísticas combinadas de jugadores
combined_df = get_combined_stats(conn, season_selected, team_selected)

# Seleccionar un jugador
players = players_df['Player'].unique()
player_selected = st.selectbox('Selecciona un jugador para comparar su desempeño', players)

# Cálculo de percentiles
combined_df = calculate_percentiles(combined_df, ['shooting_Sh', 'shooting_SoT/90', 'gca_SCA90', 'possession_Att Pen', 'possession_Succ', 'passing_Att', 'passing_Cmp',
                                                   'passing_KP', 'passing_PrgP', 'possession_Rec', 'misc_TklW',
                                                   'misc_Int', 'misc_Recov', 'misc_Fls', 'misc_Won'], season_selected)

# Diccionario de renombre de columnas
rename_dict = {
    'Percentil_shooting_Sh': 'Tiros',
    'Percentil_shooting_SoT/90': 'Tiros a puerta por 90',
    'Percentil_gca_SCA90': 'Acciones de creación por 90',
    'Percentil_possession_Att Pen': 'Toques en el área',
    'Percentil_possession_Succ': 'Regates exitosos',
    'Percentil_passing_Att': 'Pases intentados',
    'Percentil_passing_Cmp': 'Pases completados',
    'Percentil_passing_KP': 'Pases clave',
    'Percentil_passing_PrgP': 'Pases progresivos',
    'Percentil_possession_Rec': 'Recepciones',
    'Percentil_misc_TklW': 'Entradas ganadas',
    'Percentil_misc_Int': 'Intercepciones',
    'Percentil_misc_Recov': 'Recuperaciones',
    'Percentil_misc_Fls': 'Faltas cometidas',
    'Percentil_misc_Won': 'Duelos aéreos ganados'
}

# Mostrar gráfico con los datos del jugador seleccionado
st.write(f"Gráfico de pizza de desempeño para **{player_selected}**")
# Obtener los datos con percentiles calculados
percentile_df = get_percentile_data(conn, season_selected, team_selected)
# Filtrar datos del jugador seleccionado
player_data = percentile_df[percentile_df['Player'] == player_selected]
fig = pizza_chart(combined_df, player_selected, season_selected, team_selected, players_df.loc[players_df['Player'] == player_selected, 'Pos'].values[0], rename_dict)

# Mostrar el gráfico en Streamlit
st.pyplot(fig)

st.write("""
**¿Qué representan los colores en el gráfico de pizza?**

**Rojo:** Métricas relacionadas al ataque (e.g., tiros, tiros a puerta).
         
**Verde:** Métricas de posesión y control (e.g., pases clave, pases progresivos).
         
**Azul:** Métricas defensivas (e.g., intercepciones, duelos aéreos ganados).
         
>Las métricas se basan en los datos oficiales de cada temporada y equipo, permitiendo un análisis actualizado y profundo. Navega entre temporadas y jugadores para descubrir y comparar cómo destaca cada uno en sus habilidades y contribuciones al equipo.
         """)

# Cerrar la conexión a la base de datos
conn.close()