from fastapi import APIRouter, Depends, HTTPException, Request, Header, Response
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from app.models.web_schemas import (
    IssueCredential,
    PublishCredential,
    ForwardCredential,
)
from config import settings
from app.utilities import timestamp
from app.plugins.untp import UNTP_CONTEXTS
from app.plugins import (
    BitstringStatusList,
    TractionController,
    AskarStorage,
    AskarWallet,
    OCAReader,
    OrgbookPublisher,
    PublisherRegistrar,
)
import uuid
import json
from datetime import datetime
import segno

router = APIRouter(prefix="/credentials", tags=["Credentials"])


@router.post("/forward")
async def forward_credential(request_body: ForwardCredential):
    vc = request_body.model_dump()["verifiableCredential"]
    options = request_body.model_dump()["verifiableCredential"]
    try:
        credential_registration = await AskarStorage().fetch(
            "credentialRegistration", options['credentialType']
        )
    except:
        raise HTTPException(status_code=404, detail="Unknown credential type.")

    tags = {
        "entityId": options["entityId"],
        "resourceId": options["resourceId"],
        "revoked": "0",
        "updated": "0",
    }

    await AskarStorage().store("credential", options["credentialId"], vc, tags=tags)
    # await OrgbookPublisher().forward_credential(vc, credential_registration)
    return JSONResponse(status_code=201, content={"credentialId": options["credentialId"]})


@router.post("/publish")
async def publish_credential(request_body: PublishCredential):
    credential_type = request_body.model_dump()["type"]
    try:
        credential_registration = await AskarStorage().fetch(
            "credentialRegistration", credential_type
        )
    except:
        raise HTTPException(status_code=404, detail="Unknown credential type.")
    data = {
        "core": request_body.model_dump()["coreData"],
        "subject": request_body.model_dump()["subjectData"],
        "untp": request_body.model_dump()["untpData"],
    }
    credential_id = str(uuid.uuid4())
    credential = await OrgbookPublisher().format_credential(
        data, credential_registration, credential_id
    )
    traction = TractionController()
    traction.authorize()
    vc = traction.issue_vc(credential)
    vc_jwt = traction.sign_vc_jwt(vc)

    tags = {
        "entityId": data["core"]["entityId"],
        "resourceId": data["core"]["resourceId"],
        "revoked": "0",
        "updated": "0",
    }

    await AskarStorage().store("application/vc", credential_id, vc, tags=tags)
    await AskarStorage().store("application/vc+jwt", credential_id, vc_jwt, tags=tags)
    await OrgbookPublisher().forward_credential(vc, credential_registration)
    return JSONResponse(status_code=201, content={"credentialId": vc['id']})


@router.post("/issue")
async def issue_credential(request_body: IssueCredential):
    credential = request_body.model_dump()["credential"]
    options = request_body.model_dump()["options"]

    try:
        credential_registration = await AskarStorage().fetch(
            "credentialRegistration", options["credentialType"]
        )
    except:
        raise HTTPException(status_code=404, detail="Unknown credential type.")

    # W3C type and context
    contexts = ["https://www.w3.org/ns/credentials/v2"]
    types = ["VerifiableCredential"]

    # UNTP type and context
    if "untpType" in credential_registration:
        contexts.append(UNTP_CONTEXTS[credential_registration["untpType"]])
        types.append(credential_registration["untpType"])

    # BCGov type and context
    contexts.append(credential_registration["ressources"]["context"])
    types.append(credential_registration["type"])

    credential_id = str(uuid.uuid4())
    issuer = next(
        (
            issuer
            for issuer in settings.ISSUERS
            if issuer["id"] == credential_registration["issuer"]
        ),
        None,
    )

    credential = {
        "@context": contexts,
        "type": types,
        "id": f"https://{settings.DOMAIN}/credentials/{credential_id}",
        "issuer": issuer,
        "name": credential_registration["name"],
        "description": credential_registration["description"],
    } | credential

    # TODO, find a better way to get verification method
    verification_method = credential_registration["issuer"] + "#multikey-01"

    proof_options = {
        "type": "DataIntegrityProof",
        "cryptosuite": "eddsa-jcs-2022",
        "proofPurpose": "assertionMethod",
        "verificationMethod": verification_method,
        "created": str(datetime.now().isoformat("T", "seconds")),
    }

    vc = await AskarWallet().add_proof(credential, proof_options)
    await AskarStorage().store("credential", credential_id, vc)

    return JSONResponse(status_code=201, content=vc)


@router.get("/{credential_id}")
async def get_credential(credential_id: str, request: Request):
    vc = await AskarStorage().fetch("application/vc", credential_id)
    vc_jwt = await AskarStorage().fetch("application/vc+jwt", credential_id)
    traction = TractionController()
    traction.authorize()
    # verified = traction.verify_di_proof(vc)
    if "application/vc+jwt" in request.headers["accept"]:
        return Response(content=vc_jwt, media_type="application/vc+jwt")
    elif "application/vc" in request.headers["accept"]:
        return JSONResponse(
            headers={"Content-Type": "application/vc"}, 
            content=vc
        )
    oca = OCAReader()
    with open('app/static/oca-bundles/png-title.json', 'r') as f:
        bundle = json.loads(f.read())
    context = oca.create_context(vc, bundle)
    return oca.templates.TemplateResponse(
        request=request,
        name="base.jinja",
        context= context | {
            # 'vc': json.dumps(vc, indent=2),
            'vc': vc,
            'vc_jwt': vc_jwt,
            "qrcode": segno.make(vc["id"]),
            'verified': True,
            'status': True
        }
    )
    # rendered_template = OCAReader().render(vc, None)
    # return JSONResponse(status_code=201, content=vc)


# @router.post("/credentials/status")
# async def update_credential_status(request_body: IssueCredential):
#     pass


@router.get("/status/{status_credential_id}")
async def get_status_list_credential(status_credential_id: str, request: Request):
    status_list_credential = await AskarStorage().fetch(
        "statusListCredential", status_credential_id
    )
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
