import sqlite3
def connect_db(db_name):
    return sqlite3.connect(db_name)
def list_tables(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    return [table[0] for table in tables]
def list_columns(conn, table_name):
    cursor = conn.cursor()
    # Usando comillas dobles alrededor del nombre de la tabla
    cursor.execute(f'PRAGMA table_info("{table_name}");')
    columns = cursor.fetchall()
    return [column[1] for column in columns]
def get_player_names(conn, table_name, column_name, limit=10):
    cursor = conn.cursor()
    # Asegúrate de que el nombre de la columna es correcto
    cursor.execute(f'SELECT "{column_name}" FROM "{table_name}" LIMIT {limit};')  
    players = cursor.fetchall()
    return [player[0] for player in players]
if __name__ == "__main__":
    conn = connect_db('data.db')
    # Listar tablas
    tables = list_tables(conn)
    print("Tablas disponibles:")
    for table in tables:
        print(table)
    # Cambia aquí el nombre de la tabla que quieres consultar
    table_name = '2024-2025_stats_passing'  
    columns = list_columns(conn, table_name)
    print(f"\nColumnas en la tabla {table_name}:")
    for column in columns:
        print(column)
    conn.close()
