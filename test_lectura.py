import re

def parse_txt_file(filename):
    with open(filename, 'r', encoding='latin-1') as file:
        data = file.read()
    
    users = []
    user_blocks = re.split(r"-+", data)  # Dividir por líneas de guiones
    
    for block in user_blocks:
        lines = block.strip().split('\n')
        user_data = {}
        
        for line in lines:
            line = line.strip()
            if not line or ':' not in line:  # Ignorar líneas vacías o sin ':'
                continue
            
            key, value = map(str.strip, line.split(':', 1))  # Separar clave y valor
            user_data[key] = value
        
        if user_data:  # Agregar solo si hay datos
            users.append(user_data)
    
    return users

# Ejemplo de uso
filename = 'valid_users.txt'  # Cambia esto por el nombre de tu archivo
users = parse_txt_file(filename)
users_with_dsv_email_domain = []

for user in users:
    email = user.get('mail', '')  # Obtener el mail, si no existe devuelve ''
    department = user.get('department', '')

    # Validar si el departamento contiene "ITOS" o "Regional IT"
    has_forbidden_department = re.search(r'\b(ITOS|Regional IT)\b', department, re.IGNORECASE)

    # Si el email termina en "dsv.com" y NO tiene "ITOS" o "Regional IT" en department, lo agregamos a la lista
    if email.endswith('dsv.com') and not has_forbidden_department:
        users_with_dsv_email_domain.append(email)

# Guardar los emails en un archivo .txt
output_filename = "emails_filtrados.txt"

with open(output_filename, "w", encoding="utf-8") as file:
    for email in users_with_dsv_email_domain:
        file.write(email + "\n")  # Escribir cada email en una línea

print(f"Se guardaron {len(users_with_dsv_email_domain)} emails en '{output_filename}'.")