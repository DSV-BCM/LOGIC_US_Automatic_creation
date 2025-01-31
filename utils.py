import json
import logging

def process_entries(entries):
    all_users = []
    for entry in entries:
        # Si 'entry' es un diccionario, podemos acceder directamente a sus valores
        if isinstance(entry, dict):
            entry_json = entry  # Ya es un diccionario, no necesitamos convertirlo a JSON
            
        else:
            logging.error(f"Tipo de entrada desconocido: {type(entry)}")
            continue

        # Si el JSON está como string, lo intentamos convertir
        if isinstance(entry_json, str):
            try:
                entry_json = json.loads(entry_json)
            except json.JSONDecodeError as e:
                logging.error(f"Error decodificando JSON: {e}")
                continue  

        attributes = entry_json.get("attributes", {})
        cleaned_data = {
            key: value[0] if isinstance(value, list) and value else (value if value else None)
            for key, value in attributes.items()
        }

        all_users.append(cleaned_data)  # Añadir usuarios a la lista general
    return all_users