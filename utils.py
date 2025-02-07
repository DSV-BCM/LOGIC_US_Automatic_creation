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
    db_one_access = DatabaseHandler(db_type="one_access")

    for entry in entries:
        
        email = get_string_value(entry.mail)
        params = ("US", email)
        result = db_one_access.execute_procedure_verify_exist_email(params)

        if result and any(
            "The email does not exist in the database as active and can be sent as a request to create a new user."
            in row[2] for row in result
        ):
        
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
