from fastapi import APIRouter, Depends, HTTPException, Request, Header, Response
from fastapi.responses import JSONResponse
from app.models.web_schemas import (
    IssueCredential,
    Publication,
    ForwardCredential,
)
from app.models.mongoDbRecords import CredentialRecord
from config import settings
from app.utilities import timestamp
from app.plugins import (
    BitstringStatusList,
    TractionController,
    AskarStorage,
    OCAReader,
    OrgbookPublisher,
    PublisherRegistrar,
)
from app.auth.bearer import JWTBearer
import uuid
import json
import segno

router = APIRouter(prefix="/credentials")


# @router.post("/forward", dependencies=[Depends(JWTBearer())])
# async def forward_credential(request_body: ForwardCredential):
#     vc = request_body.model_dump()["verifiableCredential"]
#     options = request_body.model_dump()["options"]
#     credential_registration = await AskarStorage().fetch(
#         "credentialRegistration", options['credentialType']
#     )

#     traction = TractionController()
#     traction.authorize()
#     vc_jwt = traction.sign_vc_jwt(vc)
#     tags = {
#         "entityId": options["entityId"],
#         "resourceId": options["resourceId"],
#         "revoked": "0",
#         "updated": "0",
#     }

#     credential_id = options['credentialId']
#     await AskarStorage().store("application/vc", credential_id, vc, tags=tags)
#     await AskarStorage().store("application/vc+jwt", credential_id, vc_jwt, tags=tags)
#     # await OrgbookPublisher().forward_credential(vc, credential_registration)
#     return JSONResponse(status_code=201, content={"credentialId": options["credentialId"]})


@router.post("/publish", tags=["Client"], dependencies=[Depends(JWTBearer())])
async def publish_credential(request_body: Publication):
    credential = request_body.model_dump()["credential"]
    credential_type = credential.get("type")

    options = request_body.model_dump()["options"]
    options["credentialId"] = options.get("credentialId") or str(uuid.uuid4())

    credential = await PublisherRegistrar().format_credential(
        credential=credential, options=options
    )

    entity_id = options.get("entityId")
    credential_id = options.get("credentialId")
    cardinality_id = options.get("cardinalityId")

    traction = TractionController()
    traction.authorize()
    vc = traction.issue_vc(credential)
    vc_jwt = traction.sign_vc_jwt(vc)

    credential_record = CredentialRecord(
        id=credential_id,
        type=credential_type,
        entity_id=entity_id,
        cardinality_id=cardinality_id,
        refresh=False,
        revocation=False,
        suspension=False,
        vc=vc,
        vc_jwt=vc_jwt,
    ).model_dump()
    await AskarStorage().store("credentialRecord", credential_id, credential_record)

    credential_registration = await AskarStorage().fetch(
        "credentialTypeRecord", credential_type
    )
    await OrgbookPublisher().forward_credential(vc, credential_registration)
    return JSONResponse(status_code=201, content={"credentialId": vc["id"]})


@router.get("/{credential_id}", tags=["Public"])
async def get_credential(credential_id: str, request: Request):
    credential_record = await AskarStorage().fetch("credentialRecord", credential_id)
    vc = credential_record["vc"]
    vc_jwt = credential_record["vc_jwt"]
    if "application/vc+jwt" in request.headers["accept"]:
        return Response(content=vc_jwt, media_type="application/vc+jwt")
    elif "application/vc" in request.headers["accept"]:
        return JSONResponse(headers={"Content-Type": "application/vc"}, content=vc)
    else:
        # traction = TractionController()
        # traction.authorize()
        # verified = traction.verify_di_proof(vc)
        # oca = OCAReader()
        # with open('app/static/oca-bundles/png-title.json', 'r') as f:
        #     bundle = json.loads(f.read())
        # context = oca.create_context(vc, bundle)
        # primary_attribute = context['values'][context['branding']['primary_attribute']]
        # secondary_attribute = context['values'][context['branding']['secondary_attribute']]
        # return oca.templates.TemplateResponse(
        #     request=request,
        #     name="base.jinja",
        #     context= context | {
        #         'title': f'{primary_attribute} | {secondary_attribute}',
        #         # 'vc': vc,
        #         'vc': json.dumps(vc, indent=2),
        #         'vc_jwt': vc_jwt,
        #         "qrcode": segno.make(vc["id"]),
        #         'verified': True,
        #         'revocation': credential_record['revocation'],
        #         'updated': False
        #     }
        # )
        return JSONResponse(headers={"Content-Type": "application/vc"}, content=vc)


# @router.post("/credentials/status", dependencies=[Depends(JWTBearer())])
# async def update_credential_status(request_body: IssueCredential):
#     pass


@router.get("/status/{status_credential_id}", tags=["Public"])
async def get_status_list_credential(status_credential_id: str, request: Request):
    status_list_record = await AskarStorage().fetch(
        "statusListRecord", status_credential_id
    )
    status_list_credential = status_list_record["credential"]
    status_list_credential["validFrom"] = timestamp()
    status_list_credential["validUntil"] = timestamp(5)
    traction = TractionController()
    traction.authorize()
    if "application/vc+jwt" in request.headers["accept"]:
        vc_jwt = traction.sign_vc_jwt(status_list_credential)
        return Response(content=vc_jwt, media_type="application/vc+jwt")
    elif "application/vc" in request.headers["accept"]:
        vc = traction.issue_vc(status_list_credential)
        return JSONResponse(headers={"Content-Type": "application/vc"}, content=vc)
    else:
        vc = traction.issue_vc(status_list_credential)
        return JSONResponse(content=vc)


# @router.post("/issue")
# async def issue_credential(request_body: IssueCredential):
#     credential = request_body.model_dump()["credential"]
#     options = request_body.model_dump()["options"]

#     try:
#         credential_registration = await AskarStorage().fetch(
#             "credentialRegistration", options["credentialType"]
#         )
#     except:
#         raise HTTPException(status_code=404, detail="Unknown credential type.")

#     issuer = next(
#         (
#             issuer
#             for issuer in settings.ISSUERS
#             if issuer["id"] == credential_registration["issuer"]
#         ),
#         None,
#     )

#     # TODO, find a better way to get verification method
#     verification_method = credential_registration["issuer"] + "#multikey-01"

#     proof_options = {
#         "type": "DataIntegrityProof",
#         "cryptosuite": "eddsa-jcs-2022",
#         "proofPurpose": "assertionMethod",
#         "verificationMethod": verification_method,
#         "created": str(datetime.now().isoformat("T", "seconds")),
#     }

#     vc = await AskarWallet().add_proof(credential, proof_options)
#     await AskarStorage().store("credential", credential_id, vc)

#     return JSONResponse(status_code=201, content=vc)
