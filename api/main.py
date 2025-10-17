from fastapi import FastAPI
import logging

from session_router import api_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('vic-api')
logger.setLevel(logging.DEBUG)

app = FastAPI(
    title="Vehicle Intake API",
    description="API de servicios para la gestión de identificaciones.",
    version="0.1.0"
)

app.include_router(api_router)
