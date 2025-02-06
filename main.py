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

    country_code = 'US'  # Country code fijo para US

    # Los tres tipos de usuarios para los cuales queremos ejecutar el proceso
    user_types = ["internals", "externals", "group"]
    #user_types = ["externals", "group"] # TEST RÁPIDO
 
    if country_code not in COUNTRY_CONFIG:
        logging.error(f"Código de país '{country_code}' no reconocido.")
        return

    try:
        logging.info(f"Buscando usuarios para el país: {country_code}")
 
        start_time = time.time()

        for user_type in user_types:
            logging.info(f"Extrayendo usuarios '{user_type}' desde LDAP...")

            users = user_manager.get_users(country_code, user_type)
 
            # Guardar resultados en archivo .txt para cada tipo
            output_file = f"ldap_results_{user_type}.txt"
            with open(output_file, "w") as txt_file:
                for user in users:
                    # Obtenemos los datos del usuario usando to_dict()
                    user_data = user.to_dict()
                    
                    # Escribimos los datos del usuario en el archivo
                    for key, value in user_data.items():
                        txt_file.write(f"{key}: {value}\n")
                    
                    # Separador entre usuarios
                    txt_file.write("\n" + "-"*50 + "\n\n")
 
            logging.info(f"Se guardaron {len(users)} usuarios del tipo '{user_type}' en el archivo '{output_file}'.")
 
        end_time = time.time()
        search_duration = end_time - start_time

        logging.info(f"La búsqueda y guardado de la información tomó {search_duration:.2f} segundos.")

    except Exception as e:
        logging.error(f"Error en el proceso: {e}")
 
    finally:
        if connection:
            connection.unbind()
            logging.info("Conexión LDAP cerrada.")
 
if __name__ == "__main__":
    main()
