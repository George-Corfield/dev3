import re

email_regex = r'''\b[a-zA-Z0-9!#$%&'"*+-/;=?^_`|]+@[a-zA-Z0-9-.]+\.[a-zA-Z]{2,}\b'''

if re.fullmatch(email_regex,'corfieldG09@berkhamsted.com'):
    print('valid')