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

    def search(self, base_dn, search_filter, attributes, paged_size=500):
        """Realiza una búsqueda en el servidor LDAP, con soporte para paginación."""
        if not self.conn:
            logging.error("Conexión no establecida.")
            return []

        # Ejecutar búsqueda con paginación
        all_results = []
        cookie = None
        total_pages = 0
        paged_size = 1000

        while True:
            # Realizamos la búsqueda
            success = self.conn.search(
                search_base=base_dn,
                search_filter=search_filter,
                attributes=attributes,
                paged_size=paged_size,
                paged_cookie=cookie  # Usamos el cookie para paginación
            )

            # Imprimimos el resultado para depuración
            logging.debug(f"Resultado de la búsqueda: {self.conn.result}")

            if success:
                total_pages += 1
                logging.info(f"Página {total_pages} procesada")

                # Agregar las entradas de esta página a all_results
                all_results.extend(self.conn.entries)

                # Verificamos si hay más páginas
                cookie = self.conn.result['controls'].get('1.2.840.113556.1.4.319', {}).get('value', {}).get('cookie', b'')
                if not cookie:
                    logging.info("No hay más páginas de resultados.")
                    break  # Si no hay cookie, hemos procesado todas las páginas
            else:
                logging.error("La búsqueda no fue exitosa.")
                break  # Si la búsqueda no es exitosa, detenemos el ciclo

        logging.info(f"Total de páginas procesadas: {total_pages}")
        logging.info(f"Total de resultados encontrados: {len(all_results)}")
        return all_results
