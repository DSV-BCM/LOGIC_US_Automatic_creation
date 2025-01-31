import json
import logging
import time
from services.ldap_connector import LDAPConnector
from services.user_manager import UserManager
from config.countries import COUNTRY_CONFIG
from config.settings import LDAP_SETTINGS
 
def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
 
    ldap_connector = LDAPConnector(LDAP_SETTINGS)
    connection = ldap_connector.connect()

    if connection:
        logging.info("Conexión LDAP establecida con éxito.")
 
    user_manager = UserManager(ldap_connector, COUNTRY_CONFIG)

    country_code = input("Ingrese el código de país (por ejemplo, US, AR): ").strip().upper()
    user_type = input("Ingrese el tipo de usuario (internals, externals, group): ").strip().lower()
 
    if country_code not in COUNTRY_CONFIG:
        logging.error(f"Código de país '{country_code}' no reconocido.")
        return
 
    if user_type not in ["internals", "externals", "group"]:
        logging.error("Tipo de usuario no válido. Usa: internals, externals o group.")
        return
 
    try:
        logging.info(f"Buscando usuarios para el país: {country_code}, tipo de usuario: {user_type}")
 
        start_time = time.time()

        logging.info(f"Extrayendo usuarios '{user_type}' desde LDAP...")
        users = user_manager.get_users(country_code, user_type)
 
        end_time = time.time()
        search_duration = end_time - start_time

        # Guardar resultados en archivo .json
        output_file = f"ldap_results_{user_type}.json"
        with open(output_file, "w") as json_file:
            json.dump([user.__dict__ for user in users], json_file, indent=4)
 
        logging.info(f"Se guardaron {len(users)} usuarios del tipo '{user_type}' en el archivo '{output_file}'.")
 
        logging.info(f"La búsqueda y guardado de la información tomó {search_duration:.2f} segundos.")

    except Exception as e:
        logging.error(f"Error en el proceso: {e}")
 
    finally:
        if connection:
            connection.unbind()
            logging.info("Conexión LDAP cerrada.")
 
 
if __name__ == "__main__":
    main()
 