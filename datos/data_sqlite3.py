from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import sqlite3

# Iniciamos el WebDriver
options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome(options=options)

# Conectamos a la base de datos SQLite (Si no existe se crea una)
conn = sqlite3.connect('C:/Users/danag.LAPTOP-A0ADBJQ7/Downloads/Clases_Diplomado/proyecto_final/datos/data.db')

# Lista de temporadas a considerar (Son todas las que estan disponibles en FBREF)
seasons = ['2024-2025', '2023-2024', '2022-2023', '2021-2022', '2020-2021', '2019-2020', '2018-2019']

# Se crea un diccionario con el ID de la tabla y su URL
urls = {
    'stats_standard': 'https://fbref.com/en/comps/9/{}/stats/Premier-League-Stats',
    'stats_keeper': 'https://fbref.com/en/comps/9/{}/keepers/Premier-League-Stats',
    'stats_keeper_adv': 'https://fbref.com/en/comps/9/{}/keepersadv/Premier-League-Stats',
    'stats_shooting': 'https://fbref.com/en/comps/9/{}/shooting/Premier-League-Stats',
    'stats_passing': 'https://fbref.com/en/comps/9/{}/passing/Premier-League-Stats',
    'stats_passing_types': 'https://fbref.com/en/comps/9/{}/passing_types/Premier-League-Stats',
    'stats_gca': 'https://fbref.com/en/comps/9/{}/gca/Premier-League-Stats',
    'stats_defense': 'https://fbref.com/en/comps/9/{}/defense/Premier-League-Stats',
    'stats_possession': 'https://fbref.com/en/comps/9/{}/possession/Premier-League-Stats',
    'stats_playing_time': 'https://fbref.com/en/comps/9/{}/playingtime/Premier-League-Stats',
    'stats_misc': 'https://fbref.com/en/comps/9/{}/misc/Premier-League-Stats'
}

# Definimos la función para cargar la tabla toamando el ID y el URL
def load_table(url, table_id):
  driver.get(url)
  WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, table_id)))
  soup = BeautifulSoup(driver.page_source, 'html.parser')
  table = soup.find(id=table_id)

  # Ajustamos los MultiIndex en los nombres de la columnas y convertimos los valores a numéricos
  if table:
    df = pd.read_html(str(table))[0]

    if isinstance(df.columns, pd.MultiIndex):
      df.columns = ['_'.join(filter(None, col)).strip() for col in df.columns]

    # Definir las columnas que deben ser texto
    text_columns = [
            'Unnamed: 0_level_0_Rk', 'Unnamed: 1_level_0_Player',
            'Unnamed: 2_level_0_Nation', 'Unnamed: 3_level_0_Pos',
            'Unnamed: 4_level_0_Squad', 'Unnamed: 5_level_0_Age',
            'Unnamed: 6_level_0_Born'
        ]

    # Renombrar las columnas eliminando el prefijo 'Unnamed: ...'
    new_column_names = {
            'Unnamed: 0_level_0_Rk': 'Rk',
            'Unnamed: 1_level_0_Player': 'Player',
            'Unnamed: 2_level_0_Nation': 'Nation',
            'Unnamed: 3_level_0_Pos': 'Pos',
            'Unnamed: 4_level_0_Squad': 'Squad',
            'Unnamed: 5_level_0_Age': 'Age',
            'Unnamed: 6_level_0_Born': 'Born'
        }
    df.rename(columns=new_column_names, inplace=True)

    for column in df.columns:
      if column not in new_column_names.values():
        df[column] = pd.to_numeric(df[column], errors='coerce')

    # Eliminar la última columna si contiene 'Matches' en su nombre
    last_column = df.columns[-1]
    if 'Matches' in last_column:
        df.drop(columns=[last_column], inplace=True)

    print(f'Columnas en {table_id}: {df.columns.tolist()}')
    return df

  else:
    print(f'No se encontró la tabla con el ID {table_id}')
    return None

# Iteramos sobre las temporadas
for season in seasons:
  for stat_name, stat_url in urls.items():
    formatted_url = stat_url.format(season)
    table_id = stat_name
    df = load_table(formatted_url, table_id)

    if df is not None:
      table_name = f'{season}_{table_id}'
      df.to_sql(table_name, conn, if_exists='replace', index=False)
      print(f'Datos de {table_name} guardados en la base de datos.')
    else:
      print(f'No se pudo obtener la tabla para {table_name}.')

# Cerramos la conección a la base de datos y el WebDriver
conn.close()
driver.quit()
print("Proceso completado, datos guardados en data.db")