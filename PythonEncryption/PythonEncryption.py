import cryptography
from cryptography.fernet import Fernet
import base64, hashlib

class Encryptor:

    def __init__(self, password):
        # generate a key from a password
        self.password = password.encode()
        self.key = hashlib.md5(self.password).hexdigest()
        self.key_64 = base64.urlsafe_b64encode(self.key.encode("utf-8"))
        self.f = Fernet(self.key_64)

    def encrypt(self, filename):
        with open(filename, "rb") as file:
            # read the plain-text data
            file_data = file.read()
            # encrypt data
            encrypted_data = self.f.encrypt(file_data)
            # write the encrypted file
            print("Encrypted data is now in your directory")
            with open(filename + ".enc", "wb") as file:
                file.write(encrypted_data)

    def decrypt(self, filename):
        with open(filename, "rb") as file:
            # read the encrypted data
            encrypted_data = file.read()
            # decrypt data
            decrypted_data = self.f.decrypt(encrypted_data)
            # print(decrypted_data)
            with open(filename + ".dec", "wb") as file:
                file.write(decrypted_data)

# create an instance of Encryptor with a password
my_encryptor = Encryptor('mypassword')

# file name
file = "C:\\Users\\USER\\OneDrive\\Desktop\\files_network\\client.py"

# encrypt it
my_encryptor.encrypt(file)


file = 'C:\\Users\\USER\\OneDrive\\Desktop\\files_network\\client.py.enc'
# decrypt it
my_encryptor.decrypt(file)
