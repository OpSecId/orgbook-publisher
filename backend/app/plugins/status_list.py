import requests, random
from config import settings
from bitstring import BitArray
import gzip, base64
import uuid
from app.plugins.askar import AskarStorage


class BitstringStatusList:
    def __init__(self):
        self.store = AskarStorage()
        self.length = 200000

    def generate(self, bitstring):
        # https://www.w3.org/TR/vc-bitstring-status-list/#bitstring-generation-algorithm
        statusListBitarray = BitArray(bin=bitstring)
        statusListCompressed = gzip.compress(statusListBitarray.bytes)
        statusList_encoded = (
            base64.urlsafe_b64encode(statusListCompressed).decode("utf-8").rstrip("=")
        )
        return statusList_encoded

    def expand(self, encoded_list):
        # https://www.w3.org/TR/vc-bitstring-status-list/#bitstring-expansion-algorithm
        statusListCompressed = base64.urlsafe_b64decode(encoded_list)
        statusListBytes = gzip.decompress(statusListCompressed)
        statusListBitarray = BitArray(bytes=statusListBytes)
        statusListBitstring = statusListBitarray.bin
        return statusListBitstring

    async def create(self, credential_registration):
        # https://www.w3.org/TR/vc-bitstring-status-list/#example-example-bitstringstatuslistcredential
        # status_list_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, self.did_key))
        # id_string = credential_registration["type"] + credential_registration["version"]
        # status_list_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, id_string))
        status_list_id = str(uuid.uuid4())
        status_list_credential = {
            "@context": [
                "https://www.w3.org/ns/credentials/v2",
            ],
            "type": ["VerifiableCredential", "BitstringStatusListCredential"],
            "id": f"https://{settings.DOMAIN}/credentials/status/{status_list_id}",
            "issuer": {"id": credential_registration["issuer"]},
            "credentialSubject": {
                "type": "BitstringStatusList",
                "encodedList": self.generate(str(0) * self.length),
                "statusPurpose": ["revocation", "suspension", "update"],
            },
        }
        try:
            await AskarStorage().store(
                "statusListCredential", status_list_id, status_list_credential
            )
            await AskarStorage().store(
                "statusListEntries", status_list_id, [0, self.length - 1]
            )
        except:
            pass
        return status_list_id
    
    async def find_index(self, status_list_id):
        storage = AskarStorage()
        status_entries = await storage.fetch("statusListEntries", status_list_id)
        # Find an unoccupied index
        status_index = random.choice(
            [e for e in range(self.length - 1) if e not in status_entries]
        )
        status_entries.append(status_index)
        await storage.update("statusListEntries", status_list_id, status_entries)
        return status_index

    async def create_entry(self, status_list_id, purpose="revocation"):
        # https://www.w3.org/TR/vc-bitstring-status-list/#example-example-statuslistcredential
        storage = AskarStorage()
        status_index = await self.find_index(status_list_id)

        status_credential = await storage.fetch("statusListCredential", status_list_id)
        credential_status_id = status_credential["id"]
        credential_status_entry = {
            "id": f"{credential_status_id}#{status_index}",
            "type": "BitstringStatusListEntry",
            "statusPurpose": purpose,
            "statusListIndex": status_index,
            "statusListCredential": status_credential["id"],
        }

        return credential_status_entry

    def get_credential_status(self, vc):
        # https://www.w3.org/TR/vc-bitstring-status-list/#validate-algorithm
        statusListIndex = vc["credentialStatus"]["statusListIndex"]
        statusListCredentialUri = vc["credentialStatus"]["statusListCredential"]

        r = requests.get(statusListCredentialUri)
        statusListCredential = r.json()
        statusListBitstring = self.expand(
            statusListCredential["credentialSubject"]["encodedList"]
        )
        statusList = list(statusListBitstring)
        credentialStatusBit = statusList[statusListIndex]
        return True if credentialStatusBit == "1" else False


#     async def change_credential_status(self, vc, statusBit, did_label, statusListCredentialId):
#         statusList_index = vc["credentialStatus"]["statusListIndex"]

#         dataKey = askar.statusCredentialDataKey(did_label, statusListCredentialId)
#         statusListCredential = await askar.fetch_data(settings.ASKAR_PUBLIC_STORE_KEY, dataKey)
#         statusListEncoded = statusListCredential["credentialSubject"]["encodedList"]
#         statusListBitstring = self.expand(statusListEncoded)
#         statusList = list(statusListBitstring)

#         statusList[statusList_index] = statusBit
#         statusListBitstring = "".join(statusList)
#         statusListEncoded = self.generate(statusListBitstring)

#         statusListCredential["credentialSubject"]["encodedList"] = statusListEncoded

#         did = vc["issuer"] if isinstance(vc["issuer"], str) else vc["issuer"]["id"]
#         verkey = agent.get_verkey(did)
#         options = {
#             "verificationMethod": f"{did}#verkey",
#             "proofPurpose": "AssertionMethod",
#         }
#         # Remove old proof
#         statusListCredential.pop("proof")
#         statusListCredential = agent.sign_json_ld(statusListCredential, options, verkey)

#         return statusListCredential


# async def get_status_list_credential(did_label, statusListCredentialId):
#     try:
#         dataKey = askar.statusCredentialDataKey(did_label, statusListCredentialId)
#         statusListCredential = await askar.fetch_data(settings.ASKAR_PUBLIC_STORE_KEY, dataKey)
#     except:
#         return ValidationException(
#             status_code=404,
#             content={"message": "Status list not found"},
#         )
#     return statusListCredential
