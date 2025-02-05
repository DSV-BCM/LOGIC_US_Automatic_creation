from ldap3 import Entry
import logging


def process_entries(entries):
    """
    Procesa las entradas LDAP y extrae los atributos clave-valor desde el formato de objeto Entry.

    :param entries: Lista de entradas obtenidas desde el servidor LDAP (en formato de objeto Entry).
    :return: Lista de diccionarios con la información procesada de cada entrada.
    """


    logging.info(f"Primeras 3 entradas antes de procesar: {entries[:3]}")
