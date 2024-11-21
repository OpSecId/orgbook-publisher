from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from app.plugins import (
    AskarStorage,
)

router = APIRouter()


@router.get("/contexts/{credential_type}/{version}", tags=["Public"])
async def get_context(credential_type: str, version: str):
    credential_record = await AskarStorage().fetch(
        "credentialTypeRecord", credential_type
    )
    if not credential_record:
        raise HTTPException(
            status_code=404,
            detail="Resource not found",
        )
    context = credential_record["context"]
    return JSONResponse(status_code=200, content=context)
