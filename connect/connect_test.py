from ldap3 import Server, Connection, ALL, Tls
import ssl
import logging
import json

# Configuración del logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


def connect_to_active_directory():
    # Datos de conexión
    server_address = "ldaps://ldaps.amer.dsv.com"
    port = 636 
    username = "MX.SVC.LDAP@MX.DSV.COM" 
    password = "2gn@f61h=79N0Y@=qzQSKW&?"  
    base_dn = "OU=DSV.COM,DC=DSV,DC=COM"  

    try:
        tls_configuration = Tls(validate=ssl.CERT_NONE)
        server = Server(server_address, port=port, use_ssl=True, get_info=ALL, tls=tls_configuration)
        connection = Connection(server, user=username, password=password, auto_bind=True)

        logging.info("Conexión exitosa al Active Directory mediante LDAPS.")

        # Imprimir información del servidor
        logging.info(f"Servidor: {server}")
        logging.info(f"Fecha y hora del servidor: {server.info.other['currentTime'][0]}")

        # Desconectar
        connection.unbind()

    except Exception as error:
        logging.error(f"Error al conectar con Active Directory: {error}")

#connect_to_active_directory()



def get_name_country(country_code):
    # Simula una función para obtener el nombre del país según el código.
    country_mapping = {
        "US": "United States",
        "MX": "Mexico"
        # Agrega otros países según sea necesario
    }
    return country_mapping.get(country_code, "Unknown")

def get_info_from_ldap(country_code):
    """
    Función para obtener información del LDAP según el código de país.
    """
    server_address = "ldaps://ldaps.amer.dsv.com"
    port = 636 
    username = "MX.SVC.LDAP@MX.DSV.COM" 
    password = "2gn@f61h=79N0Y@=qzQSKW&?" 

    country_name = get_name_country(country_code)
    if country_name == "Unknown":
        logging.error(f"Código de país '{country_code}' no reconocido.")
        return

    # Definir DN y filtros basados en el tipo de usuario
    users_type = input("Ingrese el tipo de usuario (internals, externals, group): ").strip().lower()
    if users_type == "internals":
        dn = f"OU=Users,OU={country_name},OU=Countries,OU=DSV.COM,DC=DSV,DC=COM"
        search_in = "Internals"
    elif users_type == "externals":
        dn = f"OU=External Accounts,OU={country_name},OU=Countries,OU=DSV.COM,DC=DSV,DC=COM"
        search_in = "Externals"
    elif users_type == "group":
        dn = f"OU=Users,OU=Group,OU=Countries,OU=DSV.COM,DC=DSV,DC=COM"
        search_in = "Group"
    else:
        logging.error("Tipo de usuario no válido. Usa: internals, externals o group.")
        return

    filter = "(&(objectClass=user)(division=Air & Sea))"

    # Campos requeridos
    info_required = [
        "mail",
        "userPrincipalName",
        "distinguishedname",
        "employeetype",
        "title",
        "givenname",
        "sn",
        "extensionattribute4",
        "department",
        "departmentnumber",
        "physicaldeliveryofficename",
        "manager",
        "c",
        "co",
        "employeeid",
        "telephonenumber",
        "mobile",
        "streetaddress",
        "l",
        "st",
        "postalcode",
        "company",
        "division",
        "mailNickName",
        "sAMAccountName",
        "useraccountcontrol",
        "proxyAddresses",
        "memberof",
        "accountExpires",
        "displayName",
        "extensionattribute6"
    ]

    try:
        # Configuración del servidor con LDAPS
        tls_configuration = Tls(validate=ssl.CERT_NONE)
        server = Server(server_address, port=port, use_ssl=True, get_info=ALL, tls=tls_configuration)
        connection = Connection(server, user=username, password=password, auto_bind=True)
        logging.info(f"Conexión exitosa al LDAP para {search_in} en {country_name}.")

        connection.search(
            search_base=dn,
            search_filter=filter,
            attributes=info_required
        )

        results = []

        for entry in connection.entries:
            entry_data = entry.entry_to_json()
            results.append(json.loads(entry_data))

        with open("ldap_results.json", "w") as json_file:
            json.dump(results, json_file, indent=4)

        logging.info("Resultados guardados exitosamente en 'ldap_results.json'.")

        connection.unbind()
    except Exception as e:
        logging.error(f"Error al conectar o buscar en LDAP: {e}")


get_info_from_ldap("US")
