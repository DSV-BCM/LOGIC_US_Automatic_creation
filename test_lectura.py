from services.ldap_connector import LDAPConnector
from services.user_manager import UserManager
from config.countries import COUNTRY_CONFIG
from config.settings import LDAP_SETTINGS
import logging

def algo():

    ldap_connector = LDAPConnector(LDAP_SETTINGS)
    connection = ldap_connector.connect()

    if connection:
        logging.info("Conexión LDAP establecida con éxito.")
    
    user_manager = UserManager(ldap_connector, COUNTRY_CONFIG)

    manager_email = user_manager.search_manager_email('Henning Laddach')

    print(F"Desde la funcion algo: {manager_email}")

algo()