import streamlit as st
import pandas as pd
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
        df = df[selected_columns]  # Seleccionar solo columnas importantes si se pasan
    return df

# Función para seleccionar solo las columnas necesarias
def filter_columns(df, selected_columns):
    # Asegurarse de que las columnas numéricas estén correctamente tipadas
    df = df.apply(pd.to_numeric, errors='ignore')  # Convertir automáticamente lo que se pueda a numérico
    return df[selected_columns]

# Función para crear el DataFrame de porteros
def get_goalkeeper_stats(conn, season, team):
    # Seleccionar las columnas específicas de las tablas correspondientes
    columns = ['Player', 'Pos', 'Playing Time_MP', 'Playing Time_Starts', 
               'Performance_CS', 'Performance_Saves', 'Performance_GA', 
               'Expected_PSxG+/-', 'Total_Cmp%', 'Performance_Fls', 
               'Performance_Fld', 'Performance_CrdY', 'Performance_CrdR']
    
    # Obtener datos de las tablas necesarias, seleccionando solo las columnas importantes
    keeper_stats = get_team_stats(conn, season, 'stats_keeper', team, ['Player', 'Pos', 'Playing Time_MP', 'Playing Time_Starts', 'Performance_CS', 'Performance_Saves', 'Performance_GA'])
    keeper_adv_stats = get_team_stats(conn, season, 'stats_keeper_adv', team, ['Player', 'Expected_PSxG+/-'])
    passing_stats = get_team_stats(conn, season, 'stats_passing', team, ['Player', 'Total_Cmp%'])
    misc_stats = get_team_stats(conn, season, 'stats_misc', team, ['Player', 'Performance_Fls', 'Performance_Fld', 'Performance_CrdY', 'Performance_CrdR'])
    
    # Unir las tablas por la columna "Player", evitando duplicados
    combined_df = pd.merge(keeper_stats, keeper_adv_stats, on='Player')
    combined_df = pd.merge(combined_df, passing_stats, on='Player')
    combined_df = pd.merge(combined_df, misc_stats, on='Player')
    
    # Filtrar las columnas importantes
    return filter_columns(combined_df, columns)

# Función para crear el DataFrame de jugadores de campo
def get_field_players_stats(conn, season, team):
    # Seleccionar las columnas específicas de las tablas correspondientes
    columns = ['Player', 'Pos', 'Playing Time_MP', 'Playing Time_Starts', 
               'Performance_Gls', 'Performance_Ast', 'Standard_Sh', 'Standard_SoT', 
               'Total_Cmp%', 'Tackles_TklW', 'Unnamed: 20_level_0_Int', 
               'Performance_Fls', 'Performance_Fld', 'Performance_CrdY', 'Performance_CrdR']
    
    # Obtener datos de las tablas necesarias, seleccionando solo las columnas importantes
    standard_stats = get_team_stats(conn, season, 'stats_standard', team, ['Player', 'Pos', 'Playing Time_MP', 'Playing Time_Starts', 'Performance_Gls', 'Performance_Ast'])
    shooting_stats = get_team_stats(conn, season, 'stats_shooting', team, ['Player', 'Standard_Sh', 'Standard_SoT'])
    passing_stats = get_team_stats(conn, season, 'stats_passing', team, ['Player', 'Total_Cmp%'])
    defense_stats = get_team_stats(conn, season, 'stats_defense', team, ['Player', 'Tackles_TklW', 'Unnamed: 20_level_0_Int'])
    misc_stats = get_team_stats(conn, season, 'stats_misc', team, ['Player', 'Performance_Fls', 'Performance_Fld', 'Performance_CrdY', 'Performance_CrdR'])
    
    # Unir las tablas por la columna "Player", evitando duplicados
    combined_df = pd.merge(standard_stats, shooting_stats, on='Player')
    combined_df = pd.merge(combined_df, passing_stats, on='Player')
    combined_df = pd.merge(combined_df, defense_stats, on='Player')
    combined_df = pd.merge(combined_df, misc_stats, on='Player')
    
    # Filtrar las columnas importantes
    return filter_columns(combined_df, columns)

# Configuración de Streamlit
st.title("Estadísticas de Jugadores por Temporada")

# Descripción de la funcionalidad
st.write("""
    Selecciona una temporada y equipo para explorar las estadísticas de los jugadores.
    Aquí se muestran las estadísticas de porteros y jugadores de campo de manera separada.
""")

# Conectar a la base de datos
conn = connect_db('C:/Users/danag.LAPTOP-A0ADBJQ7/Downloads/Clases_Diplomado/proyecto_final/datos/data.db')

# Selectbox para la temporada
seasons = ['2024-2025', '2023-2024', '2022-2023', '2021-2022', '2020-2021', '2019-2020', '2018-2019']  # Lista de temporadas
season_selected = st.selectbox("Selecciona la temporada", seasons)

# Obtener equipos de la temporada seleccionada
teams = sorted(list_teams_by_season(conn, season_selected))
team_selected = st.selectbox("Selecciona el equipo", teams)

# Cargar la imagen del equipo
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

# Cerrar la conexión a la base de datos
conn.close()
