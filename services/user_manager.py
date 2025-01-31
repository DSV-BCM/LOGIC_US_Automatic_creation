from models.user import User
 
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
 
        try:
            entries = self.ldap_connector.search(base_dn=dn, search_filter=search_filter, attributes=attributes)
            #print(entries) debbug data 
            print(f"Se encontraron {len(entries)} usuarios en LDAP.")
        except Exception as e:
            print(f"Error en la búsqueda LDAP: {e}")
            return []

        users = []
        for entry in entries:
            entry_json = entry.entry_to_json()
            #print(f"Tipo de entry_json: {type(entry_json)} - Valor: {entry_json}")  # Depuración

            if isinstance(entry_json, str):  
                import json
                try:
                    entry_json = json.loads(entry_json)
                except json.JSONDecodeError as e:
                    print(f"Error decodificando JSON: {e}")
                    continue  

            attributes = entry_json.get("attributes", {})

            cleaned_data = {
                key: value[0] if isinstance(value, list) and value else (value if value else None)
                for key, value in attributes.items()
            }

            users.append(User(cleaned_data)) 

        return users


