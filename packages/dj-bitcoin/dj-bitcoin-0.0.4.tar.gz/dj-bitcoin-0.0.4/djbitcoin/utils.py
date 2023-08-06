from hashlib import sha256

digits58 = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'


def decode_base58(bc, length):
    n = 0
    for char in bc:
        n = n * 58 + digits58.index(char)
    return n.to_bytes(length, 'big')


def is_bitcoin_address_valid(address):
    try:
        bcbytes = decode_base58(address, 25)
    except ValueError:
        return False
    return bcbytes[-4:] == sha256(sha256(bcbytes[:-4]).digest()).digest()[:4]
