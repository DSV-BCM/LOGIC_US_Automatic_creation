
from ldap3.core.exceptions import LDAPException
from utils import process_entries
import logging

class UserManager:
    def __init__(self, ldap_connector, country_config):
        self.ldap_connector = ldap_connector
        self.country_config = country_config

    def get_users(self, country_code, user_type):
        if country_code not in self.country_config:
            raise ValueError(f"Código de país '{country_code}' no encontrado en la configuración.")
       
        country_config = self.country_config[country_code]

        user_type = user_type.strip().lower()
        
        # Verificar si el tipo de usuario es válido
        key = f"dn_{user_type}"
        if key not in country_config:
            raise ValueError(f"Tipo de usuario '{user_type}' no encontrado para el país '{country_code}'.")
        
        dn = country_config[key]

        # Filtro de búsqueda y atributos
        search_filter = "(&(objectClass=user)(division=Air & Sea))"
        attributes = [
            "mail",
            "userPrincipalName",
            "distinguishedName",
            "employeeType",
            "title",
            "givenName",
            "sn",
            "extensionAttribute4",
            "department",
            "departmentNumber",
            "physicaldeliveryofficename",
            "manager",
            "c",
            "co",
            "employeeID",
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
            "userAccountControl",
            "accountExpires",
            "displayName",
            "extensionAttribute6",
        ]
        
        all_users = []
        
        try:
            entries = self.ldap_connector.search(
                dn, 
                search_filter, 
                attributes, 
                paged_size=1000
            )

            logging.info(f"Entradas antes de procesar: {len(entries)}")
            
            all_users.extend(process_entries(entries))

            logging.info(f"Usuarios después de procesar: {len(all_users)}")

        except LDAPException as e:
            print(f"Error en la búsqueda LDAP: {e}")
        
        return all_users
