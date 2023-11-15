import bcrypt

# example password
password = 'passwordabc'

# Encode password into a readable utf-8 byte code
bytes = password.encode('utf-8')
print(bytes)

# generating the salt
salt = bcrypt.gensalt()

# Hashing the password
hash = bcrypt.hashpw(bytes, salt)
print(hash)

# Taking user entered password
userPassword = 'password123'

# encoding user password
userBytes = userPassword.encode('utf-8')
print(userBytes)

# checking password
result = bcrypt.checkpw(userBytes, hash)
print(result)
