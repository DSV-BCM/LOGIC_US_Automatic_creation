import logging
from models.user import User

def process_entries(entries):
    """
    Procesa las entradas LDAP y extrae los atributos clave-valor desde el formato de objeto Entry,
    creando instancias de la clase User para cada entrada.

    :param entries: Lista de entradas obtenidas desde el servidor LDAP (en formato de objeto Entry).
    :return: Lista de objetos User creados a partir de las entradas.
    """
    #logging.info(f"Primeras 3 entradas antes de procesar: {entries[:3]}") 

    users = []  # Lista para almacenar las instancias de User

    # Recorrer cada entrada
    for entry in entries:

        # Si 'entry' es un objeto con atributos (no un diccionario), lo accedes así:
        data = {
            "mail": entry.mail,
            "userPrincipalName": entry.userPrincipalName,
            "distinguishedName": entry.distinguishedName,
            "employeeType": entry.employeeType,
            "title": entry.title,
            "givenName": entry.givenName,
            "sn": entry.sn,
            "extensionAttribute4": entry.extensionAttribute4,
            "department": entry.department,
            "departmentNumber": entry.departmentNumber,
            "physicaldeliveryofficename": entry.physicaldeliveryofficename,
            "manager": entry.manager,
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
            "accountExpires": entry.accountExpires,
            "displayName": entry.displayName,
            "extensionAttribute6": entry.extensionAttribute6
        }

        # Crear un objeto User con los datos
        user = User(data)
        
        # Añadir el usuario a la lista
        users.append(user)

    return users
