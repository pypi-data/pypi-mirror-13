# SecretStorage module for Python
# Access passwords using the SecretService DBus API
# Author: Dmitry Shachnev, 2014
# License: BSD

'''This module contains needed classes, functions and constants
to implement dh-ietf1024-sha256-aes128-cbc-pkcs7 secret encryption
algorithm.'''

import hmac
import math

from hashlib import sha256
from Crypto.Random.random import getrandbits

# A standard 1024 bits (128 bytes) prime number for use in Diffie-Hellman exchange
DH_PRIME_1024_BYTES = (
	0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xC9, 0x0F, 0xDA, 0xA2, 0x21, 0x68, 0xC2, 0x34,
	0xC4, 0xC6, 0x62, 0x8B, 0x80, 0xDC, 0x1C, 0xD1, 0x29, 0x02, 0x4E, 0x08, 0x8A, 0x67, 0xCC, 0x74,
	0x02, 0x0B, 0xBE, 0xA6, 0x3B, 0x13, 0x9B, 0x22, 0x51, 0x4A, 0x08, 0x79, 0x8E, 0x34, 0x04, 0xDD,
	0xEF, 0x95, 0x19, 0xB3, 0xCD, 0x3A, 0x43, 0x1B, 0x30, 0x2B, 0x0A, 0x6D, 0xF2, 0x5F, 0x14, 0x37,
	0x4F, 0xE1, 0x35, 0x6D, 0x6D, 0x51, 0xC2, 0x45, 0xE4, 0x85, 0xB5, 0x76, 0x62, 0x5E, 0x7E, 0xC6,
	0xF4, 0x4C, 0x42, 0xE9, 0xA6, 0x37, 0xED, 0x6B, 0x0B, 0xFF, 0x5C, 0xB6, 0xF4, 0x06, 0xB7, 0xED,
	0xEE, 0x38, 0x6B, 0xFB, 0x5A, 0x89, 0x9F, 0xA5, 0xAE, 0x9F, 0x24, 0x11, 0x7C, 0x4B, 0x1F, 0xE6,
	0x49, 0x28, 0x66, 0x51, 0xEC, 0xE6, 0x53, 0x81, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF
)

if hasattr(int, 'from_bytes'):
	bytes_to_long = lambda bytes_array: int.from_bytes(bytes_array, 'big')
else:
	from Crypto.Util.number import bytes_to_long as _to_long
	# We need to support both list and bytes input
	bytes_to_long = lambda b: _to_long(bytes(bytearray(b)))

if hasattr(int, 'to_bytes'):
	def long_to_bytes(number):
		return int.to_bytes(number,
			math.ceil(number.bit_length() / 8), 'big')
else:
	from Crypto.Util.number import long_to_bytes

DH_PRIME_1024 = bytes_to_long(DH_PRIME_1024_BYTES)

class Session(object):
	def __init__(self):
		self.object_path = None
		self.server_public_key = None
		self.aes_key = None
		self.encrypted = True
		# 128-bytes-long strong random number
		self.my_private_key = getrandbits(0x400)
		self.my_public_key = pow(2, self.my_private_key, DH_PRIME_1024)

	def set_server_public_key(self, server_public_key):
		common_secret = pow(server_public_key, self.my_private_key,
			DH_PRIME_1024)
		common_secret = long_to_bytes(common_secret)
		# Prepend NULL bytes if needed
		common_secret = b'\x00' * (0x80 - len(common_secret)) + common_secret
		# HKDF with null salt, empty info and SHA-256 hash
		salt = b'\x00' * 0x20
		pseudo_random_key = hmac.new(salt, common_secret, sha256).digest()
		output_block = hmac.new(pseudo_random_key, b'\x01', sha256).digest()
		# Resulting AES key should be 128-bit
		self.aes_key = output_block[:0x10]
