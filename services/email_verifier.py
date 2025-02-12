from services.database_handler import DatabaseHandler

class EmailVerifier:
    def __init__(self):
        self.db = DatabaseHandler(db_type="one_access")

    def check_email_in_db(self, email, country_code):
        """
        Verifica si el email existe en la base de datos usando el procedimiento almacenado.
        """
        params = (country_code, email)
        return self.db.execute_procedure_verify_exist_email(params)
