import argparse

import sys
import pycaesar


def usage():
    print('\t\t\t Pycaesar\n\n')
    print('Usage: pycaesar -k key -m message')
    print('-k --key                - key is a numeric value to encrypt the message. Mandatory.')
    print('-m --message            - message that is going to be encrypted. Mandatory')
    print('\n\nExamples:\n pycaesar encrypt 3 \'my super message that is going to be encrypted\'')
    sys.exit(0)


def parse_args():
    parser = argparse.ArgumentParser(
        prog='Pycaesar',
        description='A simple caesar cipher in python',
        epilog='And that is the way you encrypt/decrypt data using the caesar cipher algorithm'
    )
    group_request = parser.add_argument_group('Encryption options')
    group_request.add_argument(
        'function',
        choices=['encrypt', 'decrypt'],
        help="Encrypt or decrypt?")
    group_request.add_argument(
        'key',
        type=int,
        help="Key is a numeric value to encrypt the message")
    group_request.add_argument(
        'message',
        type=str,
        help='Message to be encrypted')
    args = parser.parse_args()
    return args


def main():
    if not len(sys.argv[1:]):
        usage()
    args = parse_args()
    if args.function == 'encrypt':
        cipher_text = pycaesar.encrypt(message=args.message, key=args.key)
        print('Cipher text: {}'.format(cipher_text))
    else:
        cipher_text = pycaesar.decrypt(cipher_text=args.message, key=args.key)
        print('Plain text: {}'.format(cipher_text))


if __name__ == "__main__":
    main()
