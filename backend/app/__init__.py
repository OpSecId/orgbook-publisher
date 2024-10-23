import logging
from fastapi import FastAPI, APIRouter
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.routers import registrations, credentials, integration
from config import settings

app = FastAPI(title=settings.PROJECT_TITLE, version=settings.PROJECT_VERSION)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_router = APIRouter()


@api_router.get("/server/status", tags=["Server"], include_in_schema=False)
async def server_status():
    settings.LOGGER.info("Server status OK!")
    return JSONResponse(status_code=200, content={"status": "ok"})


api_router.include_router(integration.router)
api_router.include_router(credentials.router)
api_router.include_router(registrations.router)


app.include_router(api_router)
