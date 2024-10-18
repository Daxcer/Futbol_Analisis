from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import sqlite3
import time

# Inicializamos el WebDriver
options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome(options=options)

# Conectamos a la base de datos SQLite (si no existe, se crea automáticamente)
conn = sqlite3.connect('C:/Users/danag.LAPTOP-A0ADBJQ7/Downloads/Clases_Diplomado/proyecto_final/datos/data.db')

# Lista de temporadas
seasons = ['2024-2025', '2023-2024', '2022-2023', '2021-2022', '2020-2021', '2019-2020', '2018-2019']

# URLs para cada estadística
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

# Función para cargar una tabla de una URL y un ID específico
def load_table(url, table_id):
    driver.get(url)
    # Esperamos hasta que la tabla se cargue completamente
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, table_id)))
    # Parseamos el contenido con BeautifulSoup
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    
    # Buscamos la tabla por su ID
    table = soup.find('table', {'id': table_id})
    
    # Convertimos la tabla en un DataFrame de pandas
    if table:
        df = pd.read_html(str(table))[0]
        
        # Si existe un MultiIndex, concatenamos los niveles del índice para formar nombres únicos
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = ['_'.join(filter(None, col)).strip() for col in df.columns]
        
        # Imprimir los nombres de las columnas para revisar
        print(f'Columnas en {table_id}: {df.columns.tolist()}')
        return df
    else:
        return None

# Iteramos sobre las temporadas
for season in seasons:
    # Iteramos sobre las URLs de cada estadística
    for stat_name, stat_url in urls.items():
        formatted_url = stat_url.format(season)  # Reemplazamos con la temporada
        # El ID de la tabla es el nombre de la estadística (ej. 'stats_shooting')
        table_id = stat_name
        # Cargamos la tabla
        print(f'Cargando datos de {stat_name} para la temporada {season}...')
        df = load_table(formatted_url, table_id)
        
        if df is not None:
            # Guardamos el DataFrame en la base de datos SQLite
            table_name = f'{season}_{table_id}'
            df.to_sql(table_name, conn, if_exists='replace', index=False)
            print(f'Datos de {table_name} guardados en la base de datos.')

# Cerramos la conexión a la base de datos y el WebDriver
conn.close()
driver.quit()
print("Proceso completado, datos guardados en data.db")
