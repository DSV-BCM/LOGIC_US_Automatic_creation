from models.user import User
import re
from datetime import datetime
from config.countries import COUNTRY_CONFIG
from config.settings import LDAP_SETTINGS
import time


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
    if 'ext.' in email.lower():
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


def process_business_job_title(title, value_to_find):
    title = get_string_value(title)

    # Dividir el título en dos partes por la primera coma
    title_parts = title.split(",", 1)
    
    if len(title_parts) == 2:
        # Si hay una coma, separa el título y la descripción
        job_title = title_parts[0].strip()  # Todo lo que está antes de la primera coma
        job_description = title_parts[1].strip()  # Todo lo que está después de la primera coma
    else:
        # Si no hay coma, el título es todo el texto y la descripción es vacía
        job_title = title.strip()
        job_description = ""

    if value_to_find == "job_title":
        return job_title
    elif value_to_find == "job_description":
        return job_description
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
            "jobTitle": process_business_job_title(entry.title, "job_title"),
            "jobDescription": process_business_job_title(entry.title, "job_description"),
            "givenName": entry.givenName,
            "sn": entry.sn,
            "extensionAttribute4": int(get_string_value(entry.extensionAttribute4)), # Pasamos a entero el Security Level
            "department": entry.department,
            "departmentNumber": get_string_value(entry.departmentNumber).strip(), # Limpio espacios vacíos
            "physicaldeliveryofficename": entry.physicaldeliveryofficename,
            "manager": clean_parameter(entry.manager),
            #"managerEmail": search_manager_email(entry.manager),
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
from concurrent.futures import ThreadPoolExecutor


def fetch_manager_email(user, user_manager, cached_managers):
    """
    Función para obtener el correo del manager de un usuario de manera paralela.
    """
    user_data = user.to_dict()
    manager_email = None

    if 'manager' in user_data:
        manager_name = user_data['manager']
        manager_email = user_manager.search_manager_email(manager_name, cached_managers)
    
    # Actualizamos el campo managerEmail del objeto user
    user.managerEmail = manager_email  # Asegurándonos de que se actualiza correctamente
    
    return user  # Devolvemos solo el objeto `user` actualizado con el `managerEmail`



def process_managers_emails(valid_users):
    from services.user_manager import UserManager
    from services.ldap_connector import LDAPConnector

    ldap_connector = LDAPConnector(LDAP_SETTINGS)
    connection = ldap_connector.connect()

    if connection:
        logging.info("Conexión LDAP establecida con éxito para la búsqueda de email manager.")
    
    user_manager = UserManager(ldap_connector, COUNTRY_CONFIG)

    # Inicializamos la caché de managers
    cached_managers = {}

    # Log para verificar el número de usuarios a procesar
    logging.info(f"Se van a procesar {len(valid_users)} usuarios para verificar el email del manager.")

    start_time = time.time()
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [
            executor.submit(fetch_manager_email, user, user_manager, cached_managers) 
            for user in valid_users
        ]
        
        for future in futures:
            user = future.result()  # Ahora solo obtenemos el objeto `user` actualizado con el `managerEmail`
            # No es necesario hacer nada más, ya que `user` ya tiene el `managerEmail` actualizado

    end_time = time.time()
    search_duration = (end_time - start_time) / 60
    logging.info(f"Todas las consultas para obtener los emails de managers han terminado en {search_duration:.2f} minutos.")
    
    connection.unbind()
    logging.info("Conexión LDAP para la búsqueda de emails cerrada.")



def verify_email_for_user(user, email_verifier, country_code):
    """
    Verifica el correo electrónico de un usuario y obtiene el correo del manager si es necesario.
    """
    email = get_string_value(user.mail)
    if not email:
        return None

    result = email_verifier.check_email_in_db(email, country_code)
    if result and any("The email does not exist in the database as active" in row[2] for row in result):
        return user
    return None


def verify_emails(users, country_code):
    """
    Esta función permite verificar correos electrónicos de manera paralela, y optimiza la consulta de los correos del manager.
    """

    email_verifier = EmailVerifier()
    valid_users = []
    start_time = time.time()

    # Log para ver el número de usuarios a verificar
    logging.info(f"Iniciando verificación de emails para {len(users)} usuarios.")

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [
            executor.submit(verify_email_for_user, user, email_verifier, country_code) 
            for user in users
        ]

        for future in futures:
            user = future.result()
            if user:
                valid_users.append(user)

    end_time = time.time()
    search_duration = (end_time - start_time) / 60

    logging.info(f"Verificación de emails completada en {search_duration:.2f} minutos.")

    process_managers_emails(valid_users)  # Esto actualizará los usuarios con el managerEmail

    output_file = "valid_users.txt"
    with open(output_file, "w") as valid_file:
        for user in valid_users:
            user_data = user.to_dict()
            for key, value in user_data.items():
                valid_file.write(f"{key}: {value}\n")
            
            # Ya no necesitamos escribir el email del manager aquí, ya que está en el user.to_dict()
            # Y si se ha actualizado previamente, ya estará incluido.
            
            valid_file.write("\n" + "-"*50 + "\n\n")

    logging.info(f"✅ Se guardaron {len(valid_users)} usuarios en '{output_file}'.")

    end_time = time.time()
    search_duration = (end_time - start_time) / 60
    logging.info(f"La búsqueda de emails y guardado de la información tomó {search_duration:.2f} minutos.")
