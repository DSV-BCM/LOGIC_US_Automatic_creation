import pyodbc

class DatabaseHandler:
    def __init__(self, settings):
        self.conn_str = (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={settings['server']};DATABASE={settings['database']};"
            f"UID={settings['username']};PWD={settings['password']}"
        )

    def execute_procedure(self, procedure_name, params):
        with pyodbc.connect(self.conn_str) as conn:
            cursor = conn.cursor()
            cursor.execute(f"EXEC {procedure_name} {', '.join('?' for _ in params)}", params)
            conn.commit()