import streamlit as st
import pandas as pd
import os
import sqlite3

# Conectar a la base de datos SQLite
def connect_db(db_name):
    return sqlite3.connect(db_name)

# Obtener los equipos de una temporada
def list_teams_by_season(conn, season):
    query = f'SELECT DISTINCT "Squad" FROM "{season}_stats_standard";'
    teams = pd.read_sql_query(query, conn)
    return teams['Squad'].tolist()

# Obtener estadísticas del equipo para las tablas seleccionadas
def get_team_stats_with_cmp_percent(conn, season, table, team):
    query = f'SELECT * FROM "{season}_{table}" WHERE "Squad" = "{team}";'
    df = pd.read_sql_query(query, conn)
    
    # Calcular 'Total_Cmp%' si no está en el DataFrame
    if 'Total_Cmp%' not in df.columns:
        if 'Total_Cmp' in df.columns and 'Total_Att' in df.columns:
            df['Total_Cmp%'] = df['Total_Cmp'] / df['Total_Att'] * 100
        else:
            st.write(f"No se encontraron 'Total_Cmp' o 'Total_Att' para calcular 'Total_Cmp%' en la tabla {table}.")
    
    return df

# Mostrar porteros y jugadores de campo
def filter_and_show_stats(conn, season, team):
    # Columnas para porteros
    gk_columns = ['Player', 'Pos', 'Playing Time_MP', 'Playing Time_Starts', 
                  'Performance_CS', 'Performance_Saves', 'Performance_GA', 
                  'Expected_PSxG+/-', 'Total_Cmp%', 'Performance_Fls', 'Performance_Fld', 
                  'Performance_CrdY', 'Performance_CrdR']
    
    # Columnas para jugadores de campo
    field_columns = ['Player', 'Pos', 'Playing Time_MP', 'Playing Time_Starts', 
                     'Performance_Gls', 'Performance_Ast', 'Standard_Sh', 
                     'Standard_SoT', 'Total_Cmp%', 'Tackles_TklW', 
                     'Unnamed: 20_level_0_Int', 'Performance_Fls', 'Performance_Fld', 
                     'Performance_CrdY', 'Performance_CrdR']
    
    # Obtener estadísticas para porteros (usando varias tablas)
    gk_stats_keeper = get_team_stats_with_cmp_percent(conn, season, 'stats_keeper', team)
    gk_stats_adv = get_team_stats_with_cmp_percent(conn, season, 'stats_keeper_adv', team)
    gk_stats_passing = get_team_stats_with_cmp_percent(conn, season, 'stats_passing', team)
    gk_stats_misc = get_team_stats_with_cmp_percent(conn, season, 'stats_misc', team)
    
    # Merge de las estadísticas para porteros
    gk_df = gk_stats_keeper.merge(gk_stats_adv, on=['Player', 'Pos'], suffixes=('_x', '_y'), how='left')
    gk_df = gk_df.merge(gk_stats_passing, on=['Player', 'Pos'], suffixes=('_x', '_y'), how='left')
    gk_df = gk_df.merge(gk_stats_misc, on=['Player', 'Pos'], suffixes=('_x', '_y'), how='left')

    # Filtrar solo las columnas importantes para porteros
    gk_df_filtered = gk_df[gk_columns]
    
    # Mostrar estadísticas de porteros
    st.write(f"Estadísticas de porteros del equipo {team} en la temporada {season}")
    st.dataframe(gk_df_filtered)

    # Obtener estadísticas para jugadores de campo (usando varias tablas)
    field_stats_standard = get_team_stats_with_cmp_percent(conn, season, 'stats_standard', team)
    field_stats_shooting = get_team_stats_with_cmp_percent(conn, season, 'stats_shooting', team)
    field_stats_defense = get_team_stats_with_cmp_percent(conn, season, 'stats_defense', team)
    field_stats_misc = get_team_stats_with_cmp_percent(conn, season, 'stats_misc', team)

    # Merge de las estadísticas para jugadores de campo
    field_df = field_stats_standard.merge(field_stats_shooting, on=['Player', 'Pos'], suffixes=('_x', '_y'), how='left')
    field_df = field_df.merge(field_stats_defense, on=['Player', 'Pos'], suffixes=('_x', '_y'), how='left')
    field_df = field_df.merge(field_stats_misc, on=['Player', 'Pos'], suffixes=('_x', '_y'), how='left')

    # Filtrar solo las columnas importantes para jugadores de campo
    field_df_filtered = field_df[field_columns]
    
    # Mostrar estadísticas de jugadores de campo
    st.write(f"Estadísticas de jugadores de campo del equipo {team} en la temporada {season}")
    st.dataframe(field_df_filtered)

# Configuración de Streamlit
st.title("Estadísticas de Jugadores por Temporada")

# Descripción de la funcionalidad
st.write("""
    Selecciona una temporada y equipo para explorar las estadísticas de los jugadores.
    Además, puedes filtrar entre diferentes tipos de datos y ver el desempeño de los jugadores a profundidad.
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

# Mostrar las estadísticas de porteros y jugadores de campo
filter_and_show_stats(conn, season_selected, team_selected)

# Cerrar la conexión a la base de datos
conn.close()
