import requests
import base64
from multiformats import multibase

MULTIKEY = [
    {
        'alg': 'ed25519',
        'crv': 'Ed25519',
        'prefix': 'z6M',
        'hex_prefix': 'ed01',
        'bytes_prefix_lenght': 2
    }
]

def create_did_doc(did):
    return {}

def freeze_ressource_digest(url):
    r = requests.get(url)
    mb = ""
    return {"url": url, "digestMultibase": mb}

def verkey_to_multikey(verkey, format="ed25519"):
    multitable = {"ed25519": "ed01"}
    pass

def bytes_prefix_lenght(multikey):
    return next((item['bytes_prefix_lenght'] for item in MULTIKEY if multikey.startswith(item['prefix'])), None)

def alg_from_multikey(multikey):
    return next((item['alg'] for item in MULTIKEY if multikey.startswith(item['prefix'])), None)

def crv_from_multikey(multikey):
    return next((item['crv'] for item in MULTIKEY if multikey.startswith(item['prefix'])), None)

def get_coordinates(multikey):
    if alg_from_multikey(multikey) == 'ed25519':
        key_bytes = multibase.decode(multikey)[bytes_prefix_lenght(multikey):]
        return {'x': base64.urlsafe_b64encode(key_bytes).decode().rstrip('=')}
        
def multikey_to_jwk(multikey):
    return {
        "kty": "OKP",
        "crv": crv_from_multikey(multikey)
    } | get_coordinates(multikey)
