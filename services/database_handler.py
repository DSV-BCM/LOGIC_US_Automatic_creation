import pyodbc
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config.settings import DATABASE_SETTINGS

class DatabaseHandler:
    def __init__(self, db_type):
        """
        Inicializa la conexión a la base de datos. 
        db_type puede ser "global" o "one_access" para seleccionar la base de datos.
        """
        self.db_type = db_type
        settings = DATABASE_SETTINGS
        database_name = settings["global_database"] if db_type == "global" else settings["one_access_database"]
        
        self.conn_str = (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={settings['server']};DATABASE={database_name};"
            f"UID={settings['username']};PWD={settings['password']}"
        )

    def test_connection(self):
            try:
                with pyodbc.connect(self.conn_str) as conn:
                    print(f"Conexión exitosa a la base de datos {self.db_type}!")
                    return True
            except Exception as e:
                print(f"Error al conectar a la base de datos {self.db_type}: {e}")
                return False

    def execute_procedure_verify_exist_email(self, params):
        procedure_name = "[general].[VerifyExistEmail]"

        try:
            with pyodbc.connect(self.conn_str) as conn:
                cursor = conn.cursor()
                cursor.execute(f"EXEC {procedure_name} ?, ?", params[0], params[1])
                result = cursor.fetchall()
                conn.commit()
                return result if result else None
        except Exception as e:
            print(f"Error al ejecutar el procedimiento {procedure_name} en {self.db_type}: {e}")
            return None

# TEST procedure
""""
# Crear instancia de la conexión a la base de datos one_access
db_one_access = DatabaseHandler(db_type="one_access")

# Parámetros para el procedimiento almacenado
params = ("US", "test@example.com")

# Ejecutar el procedimiento
result = db_one_access.execute_procedure_verify_exist_email(params)

# Imprimir el resultado si existe
if result:
    for row in result:
        print(row)
else:
    print("No se encontraron resultados o hubo un error.")




TEST DE CONEXION!
# Conectarse a la base de datos global
db_global = DatabaseHandler(DATABASE_SETTINGS, db_type="global")
db_global.test_connection()

# Conectarse a la base de datos one_access
db_one_access = DatabaseHandler(DATABASE_SETTINGS, db_type="one_access")
db_one_access.test_connection()
"""