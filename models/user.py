class User:
    def __init__(self, data):
        self.mail = data.get("mail")
        self.user_principal_name = data.get("userPrincipalName")
        self.distinguished_name = data.get("distinguishedName")
        self.employee_type = data.get("employeeType")
        self.title = data.get("title")
        self.given_name = data.get("givenName")
        self.surname = data.get("sn")
        self.extension_attribute4 = data.get("extensionAttribute4")
        self.department = data.get("department")
        self.department_number = data.get("departmentNumber")
        self.office_name = data.get("physicaldeliveryofficename")
        self.manager = data.get("manager")
        self.country_code = data.get("c")
        self.country_name = data.get("co")
        self.employee_id = data.get("employeeID")
        self.telephone_number = data.get("telephonenumber")
        self.mobile_number = data.get("mobile")
        self.street_address = data.get("streetaddress")
        self.city = data.get("l")
        self.state = data.get("st")
        self.postal_code = data.get("postalcode")
        self.company = data.get("company")
        self.division = data.get("division")
        self.mail_nickname = data.get("mailNickname")
        self.sam_account_name = data.get("sAMAccountName")
        self.user_account_control = data.get("userAccountControl")
        self.account_expires = data.get("accountExpires")
        self.display_name = data.get("displayName")
        self.extension_attribute6 = data.get("extensionAttribute6")

    def __repr__(self):
        return f"<User {self.display_name} ({self.mail})>"

    def to_dict(self):
        """
        Devuelve un diccionario con los atributos del usuario de forma que sea serializable a JSON.
        """
        return {
            "mail": self.mail,
            "userPrincipalName": self.user_principal_name,
            "distinguishedName": self.distinguished_name,
            "employeeType": self.employee_type,
            "title": self.title,
            "givenName": self.given_name,
            "sn": self.surname,
            "extensionAttribute4": self.extension_attribute4,
            "department": self.department,
            "departmentNumber": self.department_number,
            "physicaldeliveryofficename": self.office_name,
            "manager": str(self.manager) if self.manager else None,  # Asegúrate de convertir a str
            "c": self.country_code,
            "co": self.country_name,
            "employeeID": self.employee_id,
            "telephonenumber": self.telephone_number,
            "mobile": self.mobile_number,
            "streetaddress": self.street_address,
            "l": self.city,
            "st": self.state,
            "postalcode": self.postal_code,
            "company": self.company,
            "division": self.division,
            "mailNickname": self.mail_nickname,
            "sAMAccountName": self.sam_account_name,
            "userAccountControl": self.user_account_control,
            "accountExpires": str(self.account_expires) if self.account_expires else None,  # Convertir a str
            "displayName": self.display_name,
            "extensionAttribute6": self.extension_attribute6
        }
