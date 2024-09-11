from fastapi import FastAPI, APIRouter, Response
from fastapi.responses import JSONResponse
from app.routers import issuers, credentials
from app.models import PublishCredential
from app.askar import AskarStorage, AskarVerifier
from config import settings

app = FastAPI(title=settings.PROJECT_TITLE, version=settings.PROJECT_VERSION)


api_router = APIRouter()

@api_router.get("/entity/{entity_id}/credentials/{credential_id}")
async def serve_credential(response: Response, entity_id: str, credential_id: str):
    vc = await AskarStorage().fetch('credential', f'{entity_id}:{credential_id}')
    response.headers['Content-Type'] = 'application/json+ld'
    return vc

@api_router.post("/credentials")
async def recieve_credential(request_body=PublishCredential):
    vp = request_body.model_dump()['verifiablePresentation']
    vp_proof = vp.pop('proof')
    await AskarVerifier().verify_proof(vp, vp_proof)
    vc = vp['verifiableCredential'][0]
    options = request_body.model_dump()['options']
    if options['credentialType'] not in vc['type']:
        pass
    entity_id = vc['id'].split('/')[-3]
    vc_id = vc['id'].split('/')[-1]
    await AskarStorage().store('credential', f'{entity_id}:{vc_id}', vc)
    return JSONResponse(status_code=201, content={"status": "ok"})


@api_router.get("/server/status", tags=["Server"], include_in_schema=False)
async def server_status():
    return JSONResponse(status_code=200, content={"status": "ok"})


app.include_router(api_router)
