import requests
import hashlib
import b58

def freeze_ressource_digest(url):
    r = requests.get(url)
    return {
        'url': url,
        'digestMultibase': f'z{b58.base58encode(hashlib.sha256(r.json()))}'
    }