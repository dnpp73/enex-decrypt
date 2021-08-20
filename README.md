Decrypt Evernote ENEX file
======


original: https://gist.github.com/gwire/0db858e055cc2bae953b435f5116aaa8
and respect: https://github.com/aviaryan/Evernote-Decrypt

Differences from the original code are as follows
- use iterator to enumerate them quickly. (regex.finditer())
- remove zero-padding from AES decrypted string.
- force utf-8 for CJK multi-byte users.
- stop using stdin. Because I wanted to use pdb.


# How to use with Docker

in host

- put your exported enex file to `./input` directory.

```
docker image build . -t enex-decrypt:latest

./docker-run.sh
```

in container

```
./enex-decrypt.py -p 'YOUR_PASSPHRASE' -i ./input/YOUR_EXPORTED_NOTES.enex -o ./output/DECRYPTED_NOTES.enex
```

check `./output/DECRYPTED_NOTES.enex`
