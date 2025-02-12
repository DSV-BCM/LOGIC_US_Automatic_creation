from models.user import User
import re
from datetime import datetime
from services.database_handler import DatabaseHandler

def clean_parameter(parameter):
    """
    Función que utilizamos para limpiar con la librería re un string y así obtener el dato que necesitamos.
    """
    if hasattr(parameter, "value"):  
        parameter = parameter.value

    if not isinstance(parameter, str):  
        return parameter

    match = re.search(r'CN=([^,]+)', parameter)
    return match.group(1) if match else parameter


def get_string_value(attribute):
    """ Convierte un atributo LDAP en un string, si existe """
    if attribute and isinstance(attribute, list):
        return str(attribute[0])
    elif attribute:
        return str(attribute)
    return ""


def format_date(date):
    """
    Función para formatear la fecha según los requisitos:
    - Si es '9999-12-31', devuelve "Never".
    - En otros casos, extrae solo la parte de la fecha (YYYY-MM-DD).
    """

    if hasattr(date, "value"):
        date = date.value

    # Confirmamos que es un objeto datetime
    if isinstance(date, datetime):
        return "Never" if date.date() in [datetime(9999, 12, 31).date(), datetime(1601, 1, 1).date()] else date.strftime("%Y-%m-%d")

    return date 


def process_entries(entries):
    """
    Procesa las entradas LDAP y extrae los atributos clave-valor desde el formato de objeto Entry,
    creando instancias de la clase User para cada entrada.

    :param entries: Lista de entradas obtenidas desde el servidor LDAP (en formato de objeto Entry).
    :return: Lista de objetos User creados a partir de las entradas.
    """

    users = []

    for entry in entries:
        
        data = {
            "mail": entry.mail,
            "userPrincipalName": entry.userPrincipalName,
            "distinguishedName": clean_parameter(entry.distinguishedName),
            "employeeType": entry.employeeType,
            "title": entry.title,
            "givenName": entry.givenName,
            "sn": entry.sn,
            "extensionAttribute4": entry.extensionAttribute4,
            "department": entry.department,
            "departmentNumber": entry.departmentNumber,
            "physicaldeliveryofficename": entry.physicaldeliveryofficename,
            "manager": clean_parameter(entry.manager),
            "c": entry.c,
            "co": entry.co,
            "employeeID": entry.employeeID,
            "telephonenumber": entry.telephonenumber,
            "mobile": entry.mobile,
            "streetaddress": entry.streetaddress,
            "l": entry.l,
            "st": entry.st,
            "postalcode": entry.postalcode,
            "company": entry.company,
            "division": entry.division,
            "mailNickname": entry.mailNickname,
            "sAMAccountName": entry.sAMAccountName,
            "userAccountControl": entry.userAccountControl,
            "accountExpires": format_date(entry.accountExpires),
            "displayName": entry.displayName,
            "extensionAttribute6": entry.extensionAttribute6
        }

        user = User(data)

        users.append(user)

    return users

import logging
from services.email_verifier import EmailVerifier
import time

def verify_emails(users, country_code):
    """
    Verifica los emails con el procedimiento almacenado y guarda los usuarios completos si cumplen la condición.
    """
    email_verifier = EmailVerifier()
    valid_users = []
    start_time = time.time()

    for user in users:
        email = get_string_value(user.mail)  # Extraemos el email del usuario
        if not email:
            continue

        
        result = email_verifier.check_email_in_db(email, country_code)

        # Si el resultado contiene el mensaje esperado, guardamos al usuario completo
        if result and any("The email does not exist in the database as active" in row[2] for row in result):
            logging.info(f"✅ El usuario {email} esta pendiente de creacion.")
            valid_users.append(user)
        else:
            logging.info(f"El usuario {email} no es candidato a creacion.")
        

    # Guardar en el archivo final solo los usuarios que pasaron el filtro
    output_file = f"valid_users.txt"
    with open(output_file, "w") as valid_file:
        for user in valid_users:
            # Obtenemos los datos del usuario usando to_dict()
            user_data = user.to_dict()

            for key, value in user_data.items():
                valid_file.write(f"{key}: {value}\n")
            valid_file.write("\n" + "-"*50 + "\n\n")  # Separador entre usuarios

    logging.info(f"✅ Se guardaron {len(valid_users)} usuarios del tipo en '{output_file}'.")

    end_time = time.time()
    search_duration = (end_time - start_time) / 60  # Convertimos a minutos
    logging.info(f"La búsqueda de emails y guardado de la información tomó {search_duration:.2f} minutos.")