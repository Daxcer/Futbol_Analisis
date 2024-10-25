import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
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

# Función para crear el DataFrame de porteros
def get_goalkeeper_stats(conn, season, team):
    columns = ['Player', 'Pos', 'Playing Time_MP', 'Playing Time_Min', 
               'Performance_CS', 'Performance_Saves', 'Performance_GA', 
               'Expected_PSxG+/-', 'Total_Cmp%', 'Performance_Fls', 
               'Performance_Fld', 'Performance_CrdY', 'Performance_CrdR']
    
    keeper_stats = get_team_stats(conn, season, 'stats_keeper', team, 
                                  ['Player', 'Pos', 'Playing Time_MP', 'Playing Time_Min', 
                                   'Performance_CS', 'Performance_Saves', 'Performance_GA'])
    keeper_adv_stats = get_team_stats(conn, season, 'stats_keeper_adv', team, ['Player', 'Expected_PSxG+/-'])
    passing_stats = get_team_stats(conn, season, 'stats_passing', team, ['Player', 'Total_Cmp%'])
    misc_stats = get_team_stats(conn, season, 'stats_misc', team, ['Player', 'Performance_Fls', 'Performance_Fld', 'Performance_CrdY', 'Performance_CrdR'])
    
    combined_df = pd.merge(keeper_stats, keeper_adv_stats, on='Player')
    combined_df = pd.merge(combined_df, passing_stats, on='Player')
    combined_df = pd.merge(combined_df, misc_stats, on='Player')
    
    return filter_columns(combined_df, columns)

# Función para crear el DataFrame de jugadores de campo
def get_field_players_stats(conn, season, team):
    columns = ['Player', 'Pos', 'Playing Time_MP', 'Playing Time_Min', 
               'Performance_Gls', 'Performance_Ast', 'Standard_Sh', 'Standard_SoT', 
               'Total_Cmp%', 'Tackles_TklW', 'Unnamed: 20_level_0_Int', 
               'Performance_Fls', 'Performance_Fld', 'Performance_CrdY', 'Performance_CrdR']
    
    standard_stats = get_team_stats(conn, season, 'stats_standard', team, ['Player', 'Pos', 'Playing Time_MP', 'Playing Time_Min', 'Performance_Gls', 'Performance_Ast'])
    shooting_stats = get_team_stats(conn, season, 'stats_shooting', team, ['Player', 'Standard_Sh', 'Standard_SoT'])
    passing_stats = get_team_stats(conn, season, 'stats_passing', team, ['Player', 'Total_Cmp%'])
    defense_stats = get_team_stats(conn, season, 'stats_defense', team, ['Player', 'Tackles_TklW', 'Unnamed: 20_level_0_Int'])
    misc_stats = get_team_stats(conn, season, 'stats_misc', team, ['Player', 'Performance_Fls', 'Performance_Fld', 'Performance_CrdY', 'Performance_CrdR'])
    
    combined_df = pd.merge(standard_stats, shooting_stats, on='Player')
    combined_df = pd.merge(combined_df, passing_stats, on='Player')
    combined_df = pd.merge(combined_df, defense_stats, on='Player')
    combined_df = pd.merge(combined_df, misc_stats, on='Player')
    
    return filter_columns(combined_df, columns)

# Función para obtener las estadísticas combinadas de un jugador
def get_combined_stats(conn, season, team):
    # Obtener datos de cada tabla relevante
    shooting_stats = get_team_stats(conn, season, 'stats_shooting', team, ['Player', 'Standard_SoT/90', 'Standard_Sh'])
    gca_stats = get_team_stats(conn, season, 'stats_gca', team, ['Player', 'SCA_SCA90'])
    possession_stats = get_team_stats(conn, season, 'stats_possession', team, ['Player', 'Touches_Att Pen', 'Take-Ons_Succ', 'Receiving_Rec'])
    passing_stats = get_team_stats(conn, season, 'stats_passing', team, ['Player', 'Total_Att', 'Total_Cmp', 'Unnamed: 26_level_0_KP', 'Unnamed: 30_level_0_PrgP'])
    misc_stats = get_team_stats(conn, season, 'stats_misc', team, ['Player', 'Performance_TklW', 'Performance_Int', 'Performance_Recov', 'Performance_Fls', 'Aerial Duels_Won'])
    standard_stats = get_team_stats(conn, season, 'stats_standard', team, ['Player', 'Pos', 'Playing Time_MP', 'Playing Time_Min'])

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
    shooting_stats = get_team_stats(conn, season, 'stats_shooting', team, ['Player', 'Squad', 'Standard_SoT/90', 'Standard_Sh'])
    gca_stats = get_team_stats(conn, season, 'stats_gca', team, ['Player', 'Squad', 'SCA_SCA90'])
    possession_stats = get_team_stats(conn, season, 'stats_possession', team, ['Player', 'Squad', 'Touches_Att Pen', 'Take-Ons_Succ', 'Receiving_Rec'])
    passing_stats = get_team_stats(conn, season, 'stats_passing', team, ['Player', 'Squad', 'Total_Att', 'Total_Cmp', 'Unnamed: 26_level_0_KP', 'Unnamed: 30_level_0_PrgP'])
    misc_stats = get_team_stats(conn, season, 'stats_misc', team, ['Player', 'Squad', 'Performance_TklW', 'Performance_Int', 'Performance_Recov', 'Performance_Fls', 'Aerial Duels_Won'])
    standard_stats = get_team_stats(conn, season, 'stats_standard', team, ['Player', 'Squad', 'Pos', 'Playing Time_MP', 'Playing Time_Min'])

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
    df['Playing Time_MP'] = pd.to_numeric(df['Playing Time_MP'], errors='coerce')
    total_matches_played = df['Playing Time_MP'].max()

    # Calcular los minutos máximos en la temporada actual
    max_minutes = get_max_minutes(season, total_matches_played)

    # Filtrar jugadores que hayan jugado al menos un % de los minutos
    df['Playing Time_Min'] = pd.to_numeric(df['Playing Time_Min'], errors='coerce')
    df = df[df['Playing Time_Min'] >= min_minutes_pct * max_minutes]

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

def plotly_radar_chart(data, player_name, season_selected, team_selected, pos, rename_dict=None):
    # Dividir las métricas en tres categorías
    attacking = ['Percentil_Standard_Sh', 'Percentil_Standard_SoT/90', 'Percentil_SCA_SCA90', 'Percentil_Touches_Att Pen', 'Percentil_Take-Ons_Succ']
    possession = ['Percentil_Total_Att', 'Percentil_Total_Cmp', 'Percentil_Unnamed: 26_level_0_KP', 'Percentil_Unnamed: 30_level_0_PrgP', 'Percentil_Receiving_Rec']
    defending = ['Percentil_Performance_TklW', 'Percentil_Performance_Int', 'Percentil_Performance_Recov', 'Percentil_Performance_Fls', 'Percentil_Aerial Duels_Won']

    metrics = attacking + possession + defending
    values = data[data['Player'] == player_name][metrics].values.flatten().tolist()

    if rename_dict:
        metrics = rename_columns(metrics, rename_dict)

    # Añadir el primer valor al final para cerrar el gráfico
    values += values[:1]
    metrics += metrics[:1]

    # Definir colores por categoría
    colors = ['#EC313A'] * len(attacking) + ['#1CD787'] * len(possession) + ['#0E70BE'] * len(defending)

    # Crear gráfico polar (radar chart) con plotly
    fig = go.Figure()

    # Dibujar segmentos individuales de colores
    for i, value in enumerate(values[:-1]):
        fig.add_trace(go.Barpolar(
            r=[100],
            theta=[metrics[i]],
            name=metrics[i],
            marker_color=colors[i],
            opacity=0.8
        ))

    # Añadir la línea principal de datos del jugador
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=metrics,
        fill='toself',
        name=player_name,
        line=dict(color='white'),
        marker=dict(color='white')
    ))

    # Configuración del gráfico y el diseño
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100], showticklabels=False),
            angularaxis=dict(showline=False)
        ),
        showlegend=False,
        title=dict(
            text=f'<b>{player_name}, {season_selected}</b>',
            font=dict(size=24),
            x=0.5,
            y=0.95,
            xanchor='center',
            yanchor='top'
        ),
        margin=dict(l=60, r=60, b=60, t=60),
        paper_bgcolor='black',  # Fondo negro
        font=dict(color='white')  # Texto blanco
    )

    # Añadir anotaciones de categorías y nota final
    fig.add_annotation(text=f'{team_selected}, {pos}', x=0.5, y=1.05, showarrow=False, font=dict(size=16, color='white'))
    fig.add_annotation(text="Rojo - Ataque", x=0.2, y=-0.15, showarrow=False, font=dict(size=12, color='#EC313A'))
    fig.add_annotation(text="Verde - Posesión", x=0.5, y=-0.15, showarrow=False, font=dict(size=12, color='#1CD787'))
    fig.add_annotation(text="Azul - Defensa", x=0.8, y=-0.15, showarrow=False, font=dict(size=12, color='#0E70BE'))
    fig.add_annotation(text="* valores convertidos a percentiles en la Premier League", x=0.5, y=-0.25, showarrow=False, font=dict(size=10, color='white', style='italic'))

    return fig


# Configuración de Streamlit
st.title("Estadísticas de Jugadores por Temporada")

# Descripción de la funcionalidad
st.write("""
    Selecciona una temporada y equipo para explorar las estadísticas de los jugadores.
    Aquí se muestran las estadísticas de porteros y jugadores de campo de manera separada.
""")

# Conectar a la base de datos
conn = connect_db('C:/Users/danag.LAPTOP-A0ADBJQ7/Downloads/Clases_Diplomado/proyecto_final/datos/data.db')

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

# Mostrar las estadísticas de porteros
st.write(f"Estadísticas de porteros del equipo {team_selected} en la temporada {season_selected}")
goalkeeper_df = get_goalkeeper_stats(conn, season_selected, team_selected)
st.dataframe(goalkeeper_df)

# Mostrar las estadísticas de jugadores de campo
st.write(f"Estadísticas de jugadores de campo del equipo {team_selected} en la temporada {season_selected}")
field_players_df = get_field_players_stats(conn, season_selected, team_selected)
st.dataframe(field_players_df)

# Obtener estadísticas combinadas de jugadores
combined_df = get_combined_stats(conn, season_selected, team_selected)

# Seleccionar un jugador
players = field_players_df['Player'].unique()
player_selected = st.selectbox('Selecciona un jugador para comparar su desempeño', players)

# Cálculo de percentiles
combined_df = calculate_percentiles(combined_df, ['Standard_Sh', 'Standard_SoT/90', 'SCA_SCA90', 'Touches_Att Pen', 'Take-Ons_Succ', 'Total_Att', 'Total_Cmp',
                                                   'Unnamed: 26_level_0_KP', 'Unnamed: 30_level_0_PrgP', 'Receiving_Rec', 'Performance_TklW',
                                                   'Performance_Int', 'Performance_Recov', 'Performance_Fls', 'Aerial Duels_Won'], season_selected)

# Diccionario de renombre de columnas
rename_dict = {
    'Percentil_Standard_Sh': 'Tiros',
    'Percentil_Standard_SoT/90': 'Tiros a puerta por 90',
    'Percentil_SCA_SCA90': 'Acciones de creación por 90',
    'Percentil_Touches_Att Pen': 'Toques en el área',
    'Percentil_Take-Ons_Succ': 'Regates exitosos',
    'Percentil_Total_Att': 'Pases intentados',
    'Percentil_Total_Cmp': 'Pases completados',
    'Percentil_Unnamed: 26_level_0_KP': 'Pases clave',
    'Percentil_Unnamed: 30_level_0_PrgP': 'Pases progresivos',
    'Percentil_Receiving_Rec': 'Recepciones',
    'Percentil_Performance_TklW': 'Entradas ganadas',
    'Percentil_Performance_Int': 'Intercepciones',
    'Percentil_Performance_Recov': 'Recuperaciones',
    'Percentil_Performance_Fls': 'Faltas cometidas',
    'Percentil_Aerial Duels_Won': 'Duelos aéreos ganados'
}

# Mostrar gráfico con los datos del jugador seleccionado
st.write(f"Gráfico de pizza de desempeño para {player_selected}")
# Obtener los datos con percentiles calculados
percentile_df = get_percentile_data(conn, season_selected, team_selected)
# Filtrar datos del jugador seleccionado
player_data = percentile_df[percentile_df['Player'] == player_selected]
fig = plotly_radar_chart(combined_df, player_selected, season_selected, team_selected, field_players_df.loc[field_players_df['Player'] == player_selected, 'Pos'].values[0], rename_dict)

# Mostrar el gráfico en Streamlit
st.plotly_chart(fig)

# Cerrar la conexión a la base de datos
conn.close()
