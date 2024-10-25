import sqlite3

# Hacemos la conexión con la base de datos
def connect_db(db_name):
  return sqlite3.connect(db_name)

# Consultamos los nombres de las tablas
def list_tables(conn):
  cursor = conn.cursor()
  cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
  tables = cursor.fetchall()
  return [table[0] for table in tables]

# Consultamos los nombres de las columnas de una tabla a elección
def list_columns(conn, table_name):
  cursor = conn.cursor()
  cursor.execute(f'PRAGMA table_info("{table_name}");')
  columns = cursor.fetchall()
  return [column[1] for column in columns]

# Consultamos los primeros 10 datos de una columna
def get_data(conn, table_name, column_name, limit=10):
  cursor = conn.cursor()
  cursor.execute(f'SELECT "{column_name}" FROM "{table_name}" LIMIT {limit};')
  data = cursor.fetchall()
  return [row[0] for row in data]

# Consultamos información de los datos
def get_data_info(conn, table_name):
  cursor = conn.cursor()

  # Obtener los nombres de las columnas y sus tipos de datos
  cursor.execute(f'PRAGMA table_info("{table_name}");')
  column_info = cursor.fetchall()
  column_names = [row[1] for row in column_info]
  column_types = [row[2] for row in column_info]

  # Contar el número de filas
  cursor.execute(f'SELECT COUNT(*) FROM "{table_name}";')
  num_rows = cursor.fetchall()

  # Imprimimos la información
  print(f'\nInformación de la tabla {table_name}')
  print('Número de filas:', num_rows)
  print('Columnas:')
  for name, type in zip(column_names, column_types):
    print(f'  {name} ({type})')

# Mostramos los nombres de las tablas
if __name__ == '__main__':
  conn = connect_db('C:/Users/danag.LAPTOP-A0ADBJQ7/Downloads/Clases_Diplomado/proyecto_final/datos/data.db')
  tables = list_tables(conn)
  for table in tables:
    print(table)

# Mostramos los nombres de las columnas de la tabla elegida
table_name = '2024-2025_stats_standard'
columns = list_columns(conn, table_name)
print(f"\nColumnas de la tabla {table_name}:")
for column in columns:
  print(column)

# Mostramos los primeros 10 datos de una columna
column_name = 'Nation'
data = get_data(conn, table_name, column_name, limit=10)
print(f"\nPrimeras 10 filas de la columna {column_name}:")
for row in data:
  print(row)

# Mostramos información de los datos
data_info = get_data_info(conn, table_name)
print(data_info)

conn.close()
