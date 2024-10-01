from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from app.models.web_schemas import RegisterIssuer
from config import settings
from app.plugins import AskarStorage, DidWebEndorser, AskarWallet
from app.models import DidDocument, VerificationMethod, Service

router = APIRouter()


@router.post("/issuers", summary="Register issuer.")
async def register_issuer(request_body: RegisterIssuer):
    name = vars(request_body)["name"]
    scope = vars(request_body)["scope"]
    description = vars(request_body)["description"]
    namespace = scope.replace(" ", "-").lower()
    identifier = name.replace(" ", "-").lower()
    did = f"did:web:{settings.DOMAIN}:{namespace}:{identifier}"
    # did_document = await DidWebEndorser().did_registration(namespace, identifier)
    did_document = DidDocument(id=did, name=name, description=description).model_dump()
    # await AskarStorage().store('didRegistration', did_document['id'], did_document)
    return JSONResponse(status_code=201, content=did_document)


# @router.get("/issuers")
# async def get_pending_issuer_registrations(did: str):
#     if did:
#         registrations = [
#             await AskarStorage().fetch('didRegistration', did)
#         ]
#     else:
#         did_registrations = []
#         registrations = [
#             await AskarStorage().fetch('didRegistration', did)
#             for did in did_registrations
#         ]
#     return JSONResponse(
#         status_code=200,
#         content={'registrations': registrations},
#     )

# @router.post("/issuers/{did}")
# async def approve_pending_issuer_registration(did: str):
#     did_document = await AskarStorage().fetch('didRegistration', did)
#     await AskarStorage().store('didDocument', did, did_document)
#     # await AskarStorage().remove('didRegistration', did)
#     return JSONResponse(
#         status_code=200,
#         content=did_document,
#     )

# @router.delete("/issuers/{did}")
# async def cancel_pending_issuer_registration(did: str):
#     # await AskarStorage().remove('didRegistration', did)
#     return JSONResponse(
#         status_code=200,
#         content={},
#     )


# @router.get("/{namespace}/{identifier}/did.json")
# async def get_issuer_did_document(namespace: str, identifier: str):
#     headers = {"Content-Type": "application/ld+json"}
#     did = f'did:web:{settings.DOMAIN}:{namespace}:{identifier}'
#     issuer = next((issuer for issuer in settings.ISSUERS if issuer['id'] == did), None)
#     # did_document = await AskarStorage().fetch('didDocument', did)
#     multikey = await AskarWallet().get_multikey(did)
#     jwk = multikey
#     did_document = DidDocument(
#         id=did,
#         name=issuer['name'],
#         description=issuer['description'],
#         authentication=[f'{did}#multikey-01'],
#         assertionMethod=[f'{did}#multikey-01'],
#         verificationMethod=[
#             VerificationMethod(
#                 type='Multikey',
#                 id=f'{did}#multikey-01',
#                 controller=did,
#                 publicKeyMultibase=multikey,
#             ),
#             VerificationMethod(
#                 type='JsonWebKey',
#                 id=f'{did}#jwk-01',
#                 controller=did,
#                 publicKeyJwk={
#                     "kty": "OKP",
#                     "crv": "Ed25519",
#                     "x": AskarWallet().multikey_to_jwk(multikey)
#                 },
#             ),
#         ],
#         service=[Service(
#             id=f'{did}#bcgov-url',
#             type='LinkedDomains',
#             serviceEndpoint=issuer['url'],
#         )]
#     ).model_dump()
#     return JSONResponse(
#         status_code=200,
#         content=did_document,
#         headers=headers
#     )
