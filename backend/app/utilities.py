import requests
import hashlib


def create_did_doc(did):
    return {}


def freeze_ressource_digest(url):
    r = requests.get(url)
    mb = ""
    return {"url": url, "digestMultibase": mb}


def verkey_to_multikey(verkey, format="ed25519"):
    multitable = {"ed25519": "ed01"}
    pass
