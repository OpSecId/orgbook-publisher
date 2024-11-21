import requests
import base64
import httpx
from multiformats import multibase
from datetime import datetime, timezone, timedelta

MULTIKEY = [
    {
        "alg": "ed25519",
        "crv": "Ed25519",
        "prefix": "z6M",
        "hex_prefix": "ed01",
        "bytes_prefix_lenght": 2,
    }
]

DEFAULT_ALG = "ed25519"
ALG_MAPPINGS = {"ed25519": {"prefix_hex": "ed01", "prefix_length": 2}}


def timestamp(minutes_forward=0):
    now = datetime.now(timezone.utc)
    delta = timedelta(minutes=minutes_forward)
    return str((now + delta).isoformat("T", "seconds"))


def create_did_doc(did):
    return {}


def freeze_ressource_digest(url):
    r = requests.get(url)
    mb = ""
    return {"url": url, "digestMultibase": mb}


def verkey_to_multikey(verkey, format="ed25519"):
    multitable = {"ed25519": "ed01"}

    prefix_hex = multitable[format]
    prefixed_key_hex = f"{prefix_hex}{multibase.decode(f'z{verkey}').hex()}"

    return multibase.encode(bytes.fromhex(prefixed_key_hex), "base58btc")


def bytes_prefix_lenght(multikey):
    return next(
        (
            item["bytes_prefix_lenght"]
            for item in MULTIKEY
            if multikey.startswith(item["prefix"])
        ),
        None,
    )


def alg_from_multikey(multikey):
    return next(
        (item["alg"] for item in MULTIKEY if multikey.startswith(item["prefix"])), None
    )


def crv_from_multikey(multikey):
    return next(
        (item["crv"] for item in MULTIKEY if multikey.startswith(item["prefix"])), None
    )


def get_coordinates(multikey):
    if alg_from_multikey(multikey) == "ed25519":
        key_bytes = multibase.decode(multikey)[bytes_prefix_lenght(multikey) :]
        return {"x": base64.urlsafe_b64encode(key_bytes).decode().rstrip("=")}


def multikey_to_jwk(multikey):
    return {"kty": "OKP", "crv": crv_from_multikey(multikey)} | get_coordinates(
        multikey
    )


def public_bytes_to_multikey(public_bytes, alg=DEFAULT_ALG):
    prefix_hex = ALG_MAPPINGS[alg]["prefix_hex"]
    return multibase.encode(
        bytes.fromhex(f"{prefix_hex}{public_bytes.hex()}"), "base58btc"
    )


def resolve_did_web(self, did):
    r = httpx.get("https://" + did.lstrip("did:web:").replace(":", "/") + "/did.json")
    return r.json()
