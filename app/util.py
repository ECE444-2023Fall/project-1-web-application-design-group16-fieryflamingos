import re

from wtforms import ValidationError

from config import Config

""" Email validation """
def validate_email(email):
    email_valid = False
    email_domain = email.rsplit("@", 1)
    if len(email_domain) != 2:
        raise  ValidationError(f"'{email}' is not a valid email.")
    email_domain_part = email_domain[-1].lower()
    for domain in Config.DOMAIN_WHITELIST:  
        if domain == email_domain_part:
            email_valid = True
            break
    if email_valid == False:
        raise ValidationError(f"'{email_domain_part}' is not a valid domain.")
    return email_valid