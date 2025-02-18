from models.user import User
import re
from datetime import datetime

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
    - Si es '9999-12-31' o '1601-01-01', devuelve "Never".
    - En otros casos, extrae solo la parte de la fecha (YYYY-MM-DD).
    """

    if hasattr(date, "value"):
        date = date.value

    if isinstance(date, datetime):
        return "Never" if date.date() in [datetime(9999, 12, 31).date(), datetime(1601, 1, 1).date()] else date.strftime("%Y-%m-%d")

    return date

def get_account_active(useraccountcontrol):
    useraccountcontrol = get_string_value(useraccountcontrol)
    if useraccountcontrol == "512" or useraccountcontrol == "66048":
        return "Enabled"
    elif useraccountcontrol == "514" or useraccountcontrol == "66050":
        return "Disabled"
    else:
        return None
    
def get_classification_user(email):
    email = get_string_value(email)
    if 'ext.' in email.lower():  # Convierto el email a minúscula antes de hacer la verificación
        return "external"
    else:
        return "internal"
    
def process_cost_center(cost_center, value_to_find):
    department_code = ""
    branch_code = ""
    
    cost_center = get_string_value(cost_center).strip()
    
    if len(cost_center) >= 3:  # Solo proceder si tiene 3 o más caracteres
        if len(cost_center) <= 5:
            department_code = cost_center[-3:] #el department_code es los últimos 3
        elif len(cost_center) >= 6:
            department_code = cost_center[-3:] 
            branch_code = cost_center[-6:-3]  # Los 3 caracteres antes para el branch_code

    if value_to_find == "branch":
        return branch_code
    elif value_to_find == "department":
        return department_code
    else:
        return None 


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
            "mail": get_string_value(entry.mail),
            "userPrincipalName": entry.userPrincipalName,
            "distinguishedName": clean_parameter(entry.distinguishedName),
            "employeeType": entry.employeeType,
            "title": entry.title,
            "givenName": entry.givenName,
            "sn": entry.sn,
            "extensionAttribute4": int(get_string_value(entry.extensionAttribute4)), # Pasamos a entero el Security Level
            "department": entry.department,
            "departmentNumber": get_string_value(entry.departmentNumber).strip(), # Limpio espacios vacíos
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
            "userAccountControl": get_account_active(entry.userAccountControl),
            "accountExpires": format_date(entry.accountExpires),
            "displayName": entry.displayName,
            "extensionAttribute6": entry.extensionAttribute6,
            "classification": get_classification_user(entry.userPrincipalName),
            "branchCode": process_cost_center(entry.departmentNumber, "branch"),
            "departmentCode": process_cost_center(entry.departmentNumber, "department")
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
        email = user.mail

        if not email:
            continue

        # Si el email existe, verificamos en BDD
        if email:
            result = email_verifier.check_email_in_db(email, country_code)

            if result and any("The email does not exist in the database as active" in row[2] for row in result):
                logging.info(f"✅ El usuario {email} esta pendiente de creacion.")
                valid_users.append(user)
            else:
                logging.info(f"El usuario {email} no es candidato a creacion.")
        

    output_file = f"valid_users.txt"
    with open(output_file, "w") as valid_file:
        for user in valid_users:
            user_data = user.to_dict()

            for key, value in user_data.items():
                valid_file.write(f"{key}: {value}\n")
            valid_file.write("\n" + "-"*50 + "\n\n")

    logging.info(f"✅ Se guardaron {len(valid_users)} usuarios del tipo en '{output_file}'.")

    end_time = time.time()
    search_duration = (end_time - start_time) / 60
    logging.info(f"La búsqueda de emails y guardado de la información tomó {search_duration:.2f} minutos.")