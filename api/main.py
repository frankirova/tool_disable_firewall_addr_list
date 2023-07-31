from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.router.routes import router 

api = FastAPI()

# Configuración CORS
origins = [
    "http://localhost:5173",
    "http://localhost:8000",
]
api.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Rutas
api.include_router(router)
