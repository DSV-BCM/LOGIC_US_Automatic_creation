
from ldap3.core.exceptions import LDAPException
from utils import process_entries
import logging
import time

class UserManager:
    def __init__(self, ldap_connector, country_config):
        self.ldap_connector = ldap_connector
        self.country_config = country_config

    def get_users(self, country_code, user_type):
        if country_code not in self.country_config:
            raise ValueError(f"Código de país '{country_code}' no encontrado en la configuración.")
       
        country_config = self.country_config[country_code]

        user_type = user_type.strip().lower()
        
        key = f"dn_{user_type}"
        if key not in country_config:
            raise ValueError(f"Tipo de usuario '{user_type}' no encontrado para el país '{country_code}'.")
        
        dn = country_config[key]

        if country_code == "US":
            # Filtro de búsqueda y atributos 
            search_filter = "(&(objectClass=user)(division=Air & Sea)(mail=*dsv.com)(!(department=*ITOS*))(!(department=*Regional IT*)))"
        else:
            search_filter = "(&(objectClass=user)(mail=*dsv.com))"
 
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
    

    def search_manager_email(self, givenname, base_dn="OU=DSV.COM,DC=DSV,DC=COM"):
        """
        Busca el email de un manager por su givenname, usando la nueva función search_email_by_givenname.
        """
        # Log para ver el inicio de la búsqueda
        logging.info(f"Iniciando búsqueda de email para el manager: {givenname}")
        
        # Usamos el filtro específico para el givenname en el atributo cn
        search_filter = f"(&(cn=*{givenname}*))"
        
        # Registramos el tiempo antes de la búsqueda LDAP
        start_time = time.time()
        results = self.ldap_connector.search_email_by_givenname(base_dn, search_filter)
        end_time = time.time()
        
        # Log para ver el tiempo que tomó la búsqueda LDAP
        logging.info(f"Búsqueda LDAP para el manager '{givenname}' completada en {end_time - start_time:.2f} segundos.")
        
        if not results:
            logging.info(f"No se encontró un manager con el givenname: {givenname}")
            return {"LDAP_MAIL": "-"}
        
        user_mail = results[0].mail if 'mail' in results[0] else "DOESNT_HAVE"
        logging.info(f"Email encontrado para el manager '{givenname}': {user_mail}")
        
        return user_mail

