from ldap3 import Server, Connection, Tls, ALL
import ssl

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
        self.conn = Connection(self.server, user=self.username, password=self.password, auto_bind=True)
        return self.conn

    def search(self, base_dn, search_filter, attributes):
        self.conn.search(search_base=base_dn, search_filter=search_filter, attributes=attributes)
        return self.conn.entries