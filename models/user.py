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
        self.classification = data.get("classification")
        self.branchCode = data.get("branchCode")
        self.departmentCode = data.get("departmentCode")

    def __repr__(self):
        return f"<User {self.display_name} ({self.mail})>"

    def to_dict(self):
        """
        Devuelve un diccionario con los atributos del usuario de forma que sea serializable a JSON.
        Si un atributo está vacío o es None, se asigna 'DOESNT_HAVE'.
        """
        def sanitize(value):
            if hasattr(value, "value"):
                value = value.value

            if value is None or value == "" or (isinstance(value, list) and not value):
                return "DOESNT_HAVE"
            
            if not isinstance(value, str):
                return value
            
            return value

        return {
            "mail": sanitize(self.mail),
            "userPrincipalName": sanitize(self.user_principal_name),
            "distinguishedName": sanitize(self.distinguished_name),
            "employeeType": sanitize(self.employee_type),
            "title": sanitize(self.title),
            "givenName": sanitize(self.given_name),
            "sn": sanitize(self.surname),
            "extensionAttribute4": sanitize(self.extension_attribute4),
            "department": sanitize(self.department),
            "departmentNumber": sanitize(self.department_number),
            "physicaldeliveryofficename": sanitize(self.office_name),
            "manager": sanitize(self.manager),
            "c": sanitize(self.country_code),
            "co": sanitize(self.country_name),
            "employeeID": sanitize(self.employee_id),
            "telephonenumber": sanitize(self.telephone_number),
            "mobile": sanitize(self.mobile_number),
            "streetaddress": sanitize(self.street_address),
            "l": sanitize(self.city),
            "st": sanitize(self.state),
            "postalcode": sanitize(self.postal_code),
            "company": sanitize(self.company),
            "division": sanitize(self.division),
            "mailNickname": sanitize(self.mail_nickname),
            "sAMAccountName": sanitize(self.sam_account_name),
            "userAccountControl": sanitize(self.user_account_control),
            "accountExpires": sanitize(self.account_expires),
            "displayName": sanitize(self.display_name),
            "extensionAttribute6": sanitize(self.extension_attribute6),
            "classification": sanitize(self.classification),
            "branchCode": sanitize(self.branchCode),
            "departmentCode": sanitize(self.departmentCode)
        }

