from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .router_global import api_router
from .database import Base, engine

app = FastAPI(
    title='Api modular FastAPI',
    description='ConstruCloudAI API',
    version='1.0.0'
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(api_router, prefix="/api/v1")

Base.metadata.create_all(bind=engine)
