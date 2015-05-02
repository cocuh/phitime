import random


def generate_salt():
    def _gen_salt():
        salt = random.randint(3, 0xFFFFFFFF)
        if salt % 2 == 0:
            salt += 1
        return salt

    salt = _gen_salt()
    return salt, _modinv(salt, 0x100000000)


def _egcd(a, b):
    if a == 0:
        return (b, 0, 1)
    else:
        g, y, x = _egcd(b % a, a)
        return (g, x - (b // a) * y, y)


def _modinv(a, m):
    g, x, y = _egcd(a, m)
    if g != 1:
        raise Exception('restart please')
    else:
        return x % m


def main():
    a, b = generate_salt()
    print("")
    print("phitime.scramble_salt: %d" % a)
    print("phitime.scramble_inverse_salt: %d" % b)