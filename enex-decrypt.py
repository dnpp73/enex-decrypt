#!/usr/bin/env python

# original: https://gist.github.com/gwire/0db858e055cc2bae953b435f5116aaa8
# and respect: https://github.com/aviaryan/Evernote-Decrypt
#
# Differences from the original code are as follows
# - use iterator to enumerate them quickly. (regex.finditer())
# - remove zero-padding from AES decrypted string.
# - force utf-8 for CJK multi-byte users.
# - stop using stdin. Because I wanted to use pdb.

# Python script to decrypt encrypted ENEX notes exported from Evernote as ENEX
#
# This will onle work on notes encypted after 2014 using the "ENC0" format
#
# This script requires a modified version of pbkdf2.py to support SHA256
#  https://github.com/PaulUithol/python-pbkdf2
#
# There's no helpful error if your password was incorrect, it will just
# echo stdin to stdout unchanged
#
# The encryption method is described by Evernote here:
#  https://help.evernote.com/hc/en-us/articles/208314128
#
# The byte-format of the ENC0 scheme is described here:
#  http://soundly.me/decoding-the-Evernote-en-crypt-field-payload/
#
# 2016-12-18 Lee Maguire

import getopt
import sys
import re
import base64
import hmac
import hashlib
from io import open

from pbkdf2 import PBKDF2
from Crypto.Cipher import AES

if sys.version_info < (3, 0):
  reload(sys)
  sys.setdefaultencoding('utf-8')

password = b'swordfish'  # It's the name of a fish
output_file = './output/decrypted.enex'

keylength = 128
iterations = 50000

opts, args = getopt.getopt(sys.argv[1:], "hp:i:o:", ["help", "password=", "input=", "output="])
for opt, arg in opts:
  if opt == '-h':
    print('Usage: en-decrypt.py -p <password> -i <input file> -o <output file>')
    sys.exit()
  elif opt in ("-p", "--password"):
    password = arg
  elif opt in ("-i", "--input"):
    with open(arg, 'r', encoding='utf-8') as f:
      input_text = f.read()
  elif opt in ("-o", "--output"):
    output_file = arg

matches = 0
decrypt_success_count = 0
decrypt_failed_count = 0
decrypt_texts = []

regex = re.compile(r'(?:<en-crypt [^>]+>)(?P<b64>[a-zA-Z0-9+/=]+)(?:</en-crypt>)')
iterator = regex.finditer(input_text)

for c in iterator:
  matches += 1
  bintxt = base64.b64decode(c.group('b64'))
  salt = bintxt[4:20]
  salthmac = bintxt[20:36]
  iv = bintxt[36:52]
  ciphertext = bintxt[52:-32]
  body = bintxt[0:-32]
  bodyhmac = bintxt[-32:]

  ## use the password to generate a digest for the encrypted body
  ## if it matches the existing digest we can assume the password is correct
  keyhmac = PBKDF2(password, salthmac, iterations, hashlib.sha256).read(keylength/8)
  testhmac = hmac.new(keyhmac, body, hashlib.sha256)
  match_hmac = hmac.compare_digest(testhmac.digest(),bodyhmac)

  if match_hmac:
    key = PBKDF2(password, salt, iterations, hashlib.sha256).read(keylength/8)
    aes = AES.new(key, AES.MODE_CBC, iv)
    decrypted = aes.decrypt(ciphertext)
    padding_bytes = decrypted[-1]
    plaintext = decrypted[:-ord(padding_bytes)] # remove padding
    decrypt_success_count += 1
    decrypt_texts.append(
      {'start': c.start(), 'end': c.end(), 'plaintext': plaintext}
    )
    print('Decrypted {} encryptions'.format(matches))
  else:
    decrypt_failed_count += 1

output_text = input_text
# reversed() is very important that editing mutable string.
for decrypt_text in reversed(decrypt_texts):
  start = decrypt_text['start']
  end = decrypt_text['end']
  plaintext = decrypt_text['plaintext']
  output_text = output_text[:start] + plaintext + output_text[end:]

with open(output_file, "w", encoding='utf-8') as f:
  f.write(output_text)

sys.exit(0 if matches > 0 else 1)
