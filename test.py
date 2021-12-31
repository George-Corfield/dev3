import re
from encryption import Hashing_algorithm
import hashlib  

email_regex = r'''\b[a-zA-Z0-9!#$%&'"*+-/;=?^_`|]+@[a-zA-Z0-9-.]+\.[a-zA-Z]{2,}\b'''

print(re.fullmatch(email_regex,'corfieldG09@berkhamsted.co'))


# password_regex = r'''^(?=(.*[A-Z]){1,})(?=(.*[a-z]){1,})(?=(.*[0-9]){1,})(?=(.*[\W]){1,}).{8,}$'''

# if re.fullmatch(password_regex,'YuoiL3748##$$'):
#     print('valid')

rooms = [[],['yes'],['not']]

for room in rooms:
    if room:
        print(room)
    else:
        pass
   