from Crypto.Cipher import AES
from getpass import getpass
import hashlib
import requests
import sys
import textwrap


IV = 16 * '\x00'
MODE = AES.MODE_CBC


def encrypt(infile, outfile, key):
    """ Encrypt a file """

    encryptor = AES.new(key, mode=MODE, IV=IV)

    with open(infile, 'r') as a:
        with open(outfile, 'wb') as b:
            message = a.read()
            padding = 16 - len(bytes(message.encode('utf-8'))) % 16
            message += '\0' * padding
            b.write(encryptor.encrypt(message))


def decrypt(message, key):
    """ Decrypt a file """

    decryptor = AES.new(key, mode=MODE, IV=IV)
    return decryptor.decrypt(message).decode('utf-8')


if __name__ == '__main__':
    
    try:
        url = sys.argv[1]
        keyfile = sys.argv[2]
    except IndexError:
        print('Usage: python oyster.py http://a/secret/url /path/to/keyfile')
        sys.exit(0)

    try:
        with open(keyfile, 'r') as f:
            key = hashlib.sha256(f.read().encode('utf-8')).digest()
    except FileNotFoundError:
        print('Keyfile not found! Please enter a valid file path.')
        sys.exit('Goodbye.')

    print("             ,%%%%%%%%,     \n"
          "           ,%%/\%%%%/\%%    \n"
          "          ,%%%\c "" J/%%%   \n"
          " %.       %%%%/ o  o \%%%   \n"
          " `%%.     %%%%    _  |%%%   \n"
          "  `%%     `%%%%(__Y__)%%'   \n"
          "  //       ;%%%%`\-/%%%'    \n"
          " ((       /  `%%%%%%%'      \n"
          "  \\    .'          |       \n"
          "   \\  /       \  | |       \n"
          "    \\/         ) | |       \n"
          "     \         /_ | |__     \n"
          "     (___________)))))))    \n"
          "                            \n")
    print("Hello traveller. I see you've got a key.")
    print("Before we try the lock, I've got one more question for you:")
    password = getpass('If one were to wear shoes... ')

    response = requests.post(url, data={'password': password})
    if response.ok:
        message = response.content
    elif response.status_code == 401:
        print('Wrong! Try again.')
        sys.exit('Goodbye.')
    else:
        print('Is your URL correct? Please double-check and try again.')
        sys.exit('Goodbye.')

    try:
        decrypted = decrypt(message, key)
    except Exception:
        print("Decryption failed! Are you sure you've got the right keyfile?")
        sys.exit('Goodbye.')

    wrapped = textwrap.wrap(decrypted, 60)
    print()
    print('\n'.join(wrapped))

