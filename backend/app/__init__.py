from fastapi import FastAPI, APIRouter
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.routers import issuers, credentials, related_resources
from config import settings

app = FastAPI(title=settings.PROJECT_TITLE, version=settings.PROJECT_VERSION)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_router = APIRouter()

api_router.include_router(issuers.router, tags=["Issuers"])
api_router.include_router(credentials.router, tags=["Credentials"])
api_router.include_router(related_resources.router, tags=["Related Resources"])


@api_router.get("/server/status", tags=["Server"], include_in_schema=False)
async def server_status():
    return JSONResponse(status_code=200, content={"status": "ok"})


app.include_router(api_router)
