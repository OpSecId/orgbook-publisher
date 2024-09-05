import json
from fastapi import HTTPException
from aries_askar import Store, error, Key
from config import settings
from app.utilities import create_did_doc
import hashlib
import uuid
from datetime import datetime, timezone, timedelta
from hashlib import sha256
import canonicaljson
from multiformats import multibase


class AskarStorage:
    def __init__(self):
        self.db = settings.ASKAR_DB
        self.key = Store.generate_raw_key(
            hashlib.md5(settings.DOMAIN.encode()).hexdigest()
        )

    async def provision(self, recreate=False):
        await Store.provision(self.db, "raw", self.key, recreate=recreate)
        issuer_registrations = {
            'issuers': []
        }
        try:
            await self.store('registration', 'issuers', issuer_registrations)
        except:
            pass

    async def open(self):
        return await Store.open(self.db, "raw", self.key)

    async def fetch(self, category, data_key):
        store = await self.open()
        try:
            async with store.session() as session:
                data = await session.fetch(category, data_key)
            return json.loads(data.value)
        except:
            return None

    async def store(self, category, data_key, data):
        store = await self.open()
        try:
            async with store.session() as session:
                await session.insert(
                    category,
                    data_key,
                    json.dumps(data),
                    {"~plaintag": "a", "enctag": "b"},
                )
        except:
            raise HTTPException(status_code=400, detail="Couldn't store record.")

    async def update(self, category, data_key, data):
        store = await self.open()
        try:
            async with store.session() as session:
                await session.replace(
                    category,
                    data_key,
                    json.dumps(data),
                    {"~plaintag": "a", "enctag": "b"},
                )
        except:
            raise HTTPException(status_code=404, detail="Couldn't update record.")
        
    async def add_issuer(self, did, name, description):
        issuer_registrations = await AskarStorage().fetch('registration', 'issuers')
        if next(
            (
                issuer
                for issuer in issuer_registrations['issuers']
                if issuer["id"]
                == did
            ),
            None,
        ):
            raise HTTPException(status_code=419, detail="Issuer already exists.")
        issuer_registrations['issuers'].append({
            'id': did,
            'name': name,
            'description': description,
        })
        issuer_registrations = await AskarStorage().update('registration', 'issuers', issuer_registrations)


class AskarVerifier:
    def __init__(self, multikey=None):
        self.type = "DataIntegrityProof"
        self.cryptosuite = "eddsa-jcs-2022"
        self.purpose = "authentication"
        if multikey:
            self.key = Key().from_public_bytes(
                alg='ed25519', public=bytes(bytearray(multibase.decode(multikey))[2:])
            )

    def create_proof_config(self):
        created = str(datetime.now(timezone.utc).isoformat("T", "seconds"))
        expires = str(
            (datetime.now(timezone.utc) + timedelta(minutes=10)).isoformat(
                "T", "seconds"
            )
        )
        return {
            "type": self.type,
            "cryptosuite": self.cryptosuite,
            "proofPurpose": self.purpose,
            "created": created,
            "expires": expires,
            "domain": settings.DOMAIN,
            "challenge": self.create_challenge(created + expires),
        }

    def create_challenge(self, value):
        return str(uuid.uuid5(uuid.NAMESPACE_DNS, settings.SECRET_KEY + value))

    def assert_proof_options(self, proof):
        try:
            assert proof["type"] == self.type
            assert proof["cryptosuite"] == self.cryptosuite
            assert proof["proofPurpose"] == self.purpose
            assert proof["domain"] == settings.DOMAIN
            # assert datetime.fromisoformat(proof["created"]) < datetime.now(timezone.utc)
            # assert datetime.fromisoformat(proof["expires"]) > datetime.now(timezone.utc)
            assert proof["challenge"] == self.create_challenge(
                proof["created"] + proof["expires"]
            )
        except:
            raise HTTPException(status_code=400, detail="Invalid Proof.")

    def verify(self, message, signature):
        return self.verifier.verify_signature(message=message, signature=signature)

    def verify_proof(self, document, proof):
        self.assert_proof_options(proof)
        assert (
            proof["verificationMethod"].split("#")[0] == document["id"]
            or proof["verificationMethod"].split("#")[0] == settings.DID_WEB_BASE
        )

        proof_options = proof.copy()
        proof_value = proof_options.pop("proofValue")
        proof_bytes = multibase.decode(proof_value)

        hash_data = (
            sha256(canonicaljson.encode_canonical_json(document)).digest()
            + sha256(canonicaljson.encode_canonical_json(proof_options)).digest()
        )

        try:
            return self.verifier.verify_signature(message=proof_bytes+hash_data, signature=None)
        except:
            raise HTTPException(
                status_code=400, detail="Signature was forged or corrupt."
            )