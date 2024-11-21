from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from app.models.registrations import IssuerRegistration, CredentialRegistration
from app.models.mongoDbRecords import (
    IssuerRecord,
    CredentialTypeRecord,
    StatusListRecord,
)
from config import settings
from app.plugins import (
    AskarStorage,
    BitstringStatusList,
    PublisherRegistrar,
    OrgbookPublisher,
)
import uuid
import random
import secrets
import hashlib
import httpx
from app.security import check_api_key_header


router = APIRouter(prefix="/registrations")


@router.post("/issuers", tags=["Admin"], dependencies=[Depends(check_api_key_header)])
async def register_issuer(request_body: IssuerRegistration):
    registration = vars(request_body)

    # Register issuer on TDW server and create DID Document
    did_document, authorized_key = await PublisherRegistrar().register_issuer(
        registration
    )

    # Create initial secret hash
    client_secret = secrets.token_urlsafe(32)
    client_hash = hashlib.sha256(client_secret.encode()).hexdigest()

    issuer = IssuerRecord(
        id=did_document["id"],
        name=registration.get("name"),
        description=registration.get("description"),
        authorized_key=authorized_key,
        secret_hash=client_hash,
        did_document=did_document,
    ).model_dump()

    await AskarStorage().replace("issuerRecord", did_document["id"], issuer)

    return JSONResponse(status_code=201, content=did_document)


@router.post(
    "/credentials", tags=["Admin"], dependencies=[Depends(check_api_key_header)]
)
async def register_credential_type(request_body: CredentialRegistration):
    credential_registration = request_body.model_dump()

    # Create a new status status list for this type of credential
    indexes = list(range(200000))
    random.shuffle(indexes)

    status_list_id = str(uuid.uuid4())
    status_list_credential = await BitstringStatusList().create(
        # id=f"https://{settings.DOMAIN}/credentials/status/{status_list_id}",
        issuer={"id": credential_registration["issuer"]},
        purpose=["revocation", "suspension", "supercession"],
        length=len(indexes),
    )

    status_list_record = StatusListRecord(
        id=status_list_id,
        indexes=indexes,
        endpoint=f"https://{settings.DOMAIN}/credentials/status/{status_list_id}",
        credential=status_list_credential,
    ).model_dump()

    await AskarStorage().store("statusListRecord", status_list_id, status_list_record)

    # Create a new template for this credential type
    credential_template = await PublisherRegistrar().template_credential(
        credential_registration
    )

    # Fetch remote context
    r = httpx.get(credential_registration["relatedResources"]["context"])
    context = r.json()
    # TODO, test context

    credential_registration = CredentialTypeRecord(
        type=credential_registration.get("type"),
        version=credential_registration.get("version"),
        issuer=credential_registration.get("issuer"),
        # schema='',
        context=context,
        core_paths=credential_registration.get("corePaths"),
        subject_type=credential_registration.get("subjectType"),
        subject_paths=credential_registration.get("subjectPaths"),
        additional_type=credential_registration.get("additionalType"),
        additional_paths=credential_registration.get("additionalPaths"),
        credential_template=credential_template,
        status_lists=[status_list_id],
    ).model_dump()
    await AskarStorage().replace(
        "credentialTypeRecord",
        credential_registration["type"],
        credential_registration,
    )

    # Register credential type with Orgbook
    # await OrgbookPublisher().create_credential_type(credential_registration)
    return JSONResponse(status_code=201, content=credential_registration)
