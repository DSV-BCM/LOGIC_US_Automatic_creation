from ldap3 import Server, Connection, Tls, ALL
import ssl
import logging

class LDAPConnector:
    def __init__(self, settings):
        self.server = Server(
            settings["server_address"],
            port=settings["port"],
            use_ssl=True,
            get_info=ALL,
            tls=Tls(validate=ssl.CERT_NONE)
        )
        self.username = settings["username"]
        self.password = settings["password"]

    def connect(self):
        """Establece la conexión con el servidor LDAP."""
        try:
            self.conn = Connection(self.server, user=self.username, password=self.password, auto_bind=True)
            return self.conn
        except Exception as e:
            logging.error(f"Error al conectar con el servidor LDAP: {e}")
            return None

    def search(self, base_dn, search_filter, attributes, paged_size=1000):
        """Realiza una búsqueda en el servidor LDAP, con soporte para paginación."""
        if not self.conn:
            logging.error("Conexión no establecida.")
            return []

        # Búsqueda con paginación
        all_results = []
        cookie = None
        total_pages = 0

        while True:
            try:
                success = self.conn.search(
                    search_base=base_dn,
                    search_filter=search_filter,
                    attributes=attributes,
                    paged_size=paged_size,
                    paged_cookie=cookie  
                )

                logging.debug(f"Resultado de la búsqueda: {self.conn.result}")

                if success:
                    total_pages += 1
                    logging.info(f"Página {total_pages} procesada")

                    all_results.extend(self.conn.entries)

                    cookie = self.conn.result['controls'].get('1.2.840.113556.1.4.319', {}).get('value', {}).get('cookie', b'')
                    if not cookie:
                        logging.info("No hay más páginas de resultados.")
                        break
                else:
                    logging.error("La búsqueda no fue exitosa.")
                    break
            except Exception as e:
                logging.error(f"Ocurrió un error durante la búsqueda: {e}")
                break

        logging.info(f"Total de páginas procesadas: {total_pages}")
        logging.info(f"Total de resultados encontrados: {len(all_results)}")
        return all_results

    def search_email_by_givenname(self, base_dn, search_filter, attributes="mail"):
        """Realiza una búsqueda LDAP para obtener el correo electrónico de un usuario."""
        if not self.conn:
            logging.error("Conexión no establecida.")
            return None

        try:
            success = self.conn.search(
                search_base=base_dn,
                search_filter=search_filter,
                attributes=attributes
            )

            if success and self.conn.entries:
                logging.info("Búsqueda LDAP exitosa.")
                entry = self.conn.entries[0]  # Tomamos el primer y único resultado
                email = entry.mail.value if hasattr(entry, "mail") else None
                

                if email:
                    logging.info(f"Correo encontrado: {email}")
                    #print(f"el mail que se encontro es: {email}")
                    return email
                else:
                    #logging.warning("No se encontró un correo electrónico en el resultado.")
                    return None
            else:
                #logging.error("La búsqueda no fue exitosa o no se encontraron resultados.")
                return None

        except Exception as e:
            logging.error(f"Ocurrió un error durante la búsqueda: {e}")
            return None
